#!/usr/bin/env python3
"""Minimal fail-closed invariant verifier for RayFlow task-state v0.1."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


STATES = [
    "CREATED",
    "DISPATCHED",
    "ACCEPTED",
    "RUNNING",
    "PRODUCED",
    "PERSISTED",
    "PUBLISHED",
    "OBSERVED",
    "ACKED",
    "VERIFIED",
    "CLOSED",
]
STATE_INDEX = {state: index for index, state in enumerate(STATES)}
HEX40 = re.compile(r"^[a-f0-9]{40}$")
HEX64 = re.compile(r"^[A-Fa-f0-9]{64}$")


def state_at_least(state: str, floor: str) -> bool:
    return state in STATE_INDEX and STATE_INDEX[state] >= STATE_INDEX[floor]


def effective_gate(record: dict) -> str:
    alarms = record.get("gate", {}).get("alarms", [])
    if any(a.get("severity") == "CRITICAL" and a.get("verdict") in {"BLOCK", "UNKNOWN"} for a in alarms):
        return "BLOCK"
    if any(a.get("evidence_ref") in {None, ""} for a in alarms):
        return "BLOCK"
    verification = record.get("verification", {})
    if verification.get("verdict") != "PASS" or not verification.get("independent_of_builder", False):
        return "BLOCK"
    if any(a.get("severity") == "NONCRITICAL" and a.get("verdict") == "DEGRADED" for a in alarms):
        return "DEGRADED"
    return "PASS"


def validate_record(record: dict) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version", "task_id", "work_package_id", "title",
        "requirement_revision", "idempotency_key", "criticality",
        "current_state", "actor", "dependencies", "artifact", "delivery",
        "verification", "gate", "lease", "recovery", "history", "updated_at",
    }
    missing = sorted(required - set(record))
    if missing:
        errors.append("E_REQUIRED:" + ",".join(missing))
        return errors

    if record["schema_version"] != "rayflow.task-state/v0.1":
        errors.append("E_SCHEMA_VERSION")
    if record["current_state"] not in STATE_INDEX:
        errors.append("E_STATE_UNKNOWN")
        return errors
    if not HEX64.fullmatch(str(record["idempotency_key"])):
        errors.append("E_IDEMPOTENCY_KEY")

    state = record["current_state"]
    artifact = record["artifact"]
    delivery = record["delivery"]
    verification = record["verification"]
    lease = record["lease"]

    if state_at_least(state, "PRODUCED") and not HEX64.fullmatch(str(artifact.get("content_sha256") or "")):
        errors.append("E_PRODUCED_WITHOUT_CONTENT_SHA")
    if state_at_least(state, "PUBLISHED") and not HEX40.fullmatch(str(artifact.get("git_commit") or "")):
        errors.append("E_PUBLISHED_WITHOUT_COMMIT")
    if state_at_least(state, "OBSERVED"):
        if delivery.get("expected_commit") != delivery.get("observed_commit"):
            errors.append("E_OBSERVED_COMMIT_MISMATCH")
        if delivery.get("expected_content_sha256") != delivery.get("observed_content_sha256"):
            errors.append("E_OBSERVED_CONTENT_MISMATCH")
        if not delivery.get("observer_agent_id") or not delivery.get("observation_method"):
            errors.append("E_OBSERVED_WITHOUT_OBSERVER")
    if state_at_least(state, "ACKED") and delivery.get("ack") != "YES":
        errors.append("E_ACK_REQUIRED")
    if state_at_least(state, "VERIFIED"):
        if verification.get("verdict") != "PASS":
            errors.append("E_VERIFICATION_NOT_PASS")
        if not verification.get("independent_of_builder", False):
            errors.append("E_VERIFIER_NOT_INDEPENDENT")
        if effective_gate(record) != "PASS":
            errors.append("E_GATE_NOT_PASS")
    if state == "CLOSED":
        if any(not d.get("satisfied", False) for d in record["dependencies"]):
            errors.append("E_DEPENDENCY_OPEN")
        if lease.get("status") not in {"NONE", "RELEASED"}:
            errors.append("E_LEASE_NOT_RELEASED")
        ray = record.get("completion_proof", {}).get("ray_acceptance")
        if record["work_package_id"].startswith("WP") and not ray:
            errors.append("E_RAY_ACCEPTANCE_REQUIRED")

    history = record["history"]
    if [event.get("sequence") for event in history] != list(range(1, len(history) + 1)):
        errors.append("E_HISTORY_SEQUENCE")
    for previous, current in zip(history, history[1:]):
        if current.get("from") != previous.get("to"):
            errors.append("E_HISTORY_LINK")
            break
    if history and history[-1].get("to") != state:
        errors.append("E_HISTORY_HEAD")
    return errors


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timezone required")
    return parsed.astimezone(timezone.utc)


def validate_peer_leases(records: list[dict]) -> list[str]:
    errors: list[str] = []
    active = [r["lease"] for r in records if r.get("lease", {}).get("status") == "ACTIVE"]
    for index, left in enumerate(active):
        for right in active[index + 1:]:
            if left.get("resource") != right.get("resource"):
                continue
            try:
                overlap = min(parse_time(left["expires_at"]), parse_time(right["expires_at"])) > max(
                    parse_time(left["heartbeat_at"]), parse_time(right["heartbeat_at"])
                )
            except (KeyError, TypeError, ValueError):
                errors.append("E_LEASE_TIME_UNKNOWN")
                continue
            if overlap:
                errors.append("E_DOUBLE_ACTIVE_LEASE:" + str(left.get("resource")))
    return errors


def validate_graph(graph: dict) -> list[str]:
    errors: list[str] = []
    nodes = graph.get("nodes", [])
    ids = [node.get("task_id") for node in nodes]
    if len(ids) != len(set(ids)):
        errors.append("E_GRAPH_DUPLICATE_NODE")
    known = set(ids)
    edges = {node.get("task_id"): node.get("depends_on", []) for node in nodes}
    for node, deps in edges.items():
        for dep in deps:
            if dep not in known:
                errors.append(f"E_GRAPH_MISSING_NODE:{node}:{dep}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            errors.append("E_GRAPH_CYCLE:" + node)
            return
        if node in visited:
            return
        visiting.add(node)
        for dep in edges.get(node, []):
            if dep in known:
                visit(dep)
        visiting.remove(node)
        visited.add(node)

    for node in ids:
        visit(node)
    return sorted(set(errors))


def base_record() -> dict:
    digest = hashlib.sha256(b"repo\nWP001-SCHEMA\nv0.1\n04_KNOWLEDGE_OS/SCHEMA_v0.1.md\nmain").hexdigest()
    return {
        "schema_version": "rayflow.task-state/v0.1",
        "task_id": "WP001-SCHEMA",
        "work_package_id": "WP001",
        "title": "Knowledge OS schema",
        "requirement_revision": "v0.1",
        "idempotency_key": digest,
        "criticality": "CRITICAL",
        "current_state": "VERIFIED",
        "actor": {"agent_id": "CODEX", "role": "BUILDER", "vendor": "OpenAI", "machine_id": "HOME-1", "site": "HOME", "session_id": "test"},
        "dependencies": [{"task_id": "WP001_SCHEMA_ACK", "required_state": "ACKED", "observed_state": "ACKED", "satisfied": True, "evidence_ref": "ack.json"}],
        "artifact": {"repository": "repo", "branch": "main", "path": "04_KNOWLEDGE_OS/SCHEMA_v0.1.md", "content_sha256": "a" * 64, "git_commit": "b" * 40},
        "delivery": {"expected_commit": "b" * 40, "observed_commit": "b" * 40, "expected_content_sha256": "a" * 64, "observed_content_sha256": "a" * 64, "observer_agent_id": "CLAUDE", "observation_method": "git-show-and-hash", "ack": "YES"},
        "verification": {"verifier_agent_id": "ADVERSARY", "method_class": "ADVERSARIAL_TEST", "independent_of_builder": True, "verdict": "PASS", "evidence_ref": "verification.json"},
        "gate": {"declared_verdict": "PASS", "computed_verdict": "PASS", "alarms": []},
        "lease": {"resource": "repo:WP001", "lease_id": None, "holder_agent_id": None, "machine_id": None, "site": "NONE", "fencing_token": 2, "heartbeat_at": None, "expires_at": None, "status": "RELEASED"},
        "recovery": {"attempt_id": "attempt-2", "previous_attempt_id": "attempt-1", "last_durable_state": "ACKED", "context_digest": "c" * 64, "resume_allowed": True},
        "history": [
            {"sequence": i + 1, "from": STATES[i - 1] if i else None, "to": state, "at": "2026-09-15T00:00:00+08:00", "evidence_ref": f"evidence-{i + 1}"}
            for i, state in enumerate(STATES[:10])
        ],
        "updated_at": "2026-09-15T00:00:00+08:00"
    }


def self_test() -> list[tuple[str, bool, str]]:
    results: list[tuple[str, bool, str]] = []

    produced = base_record()
    produced["current_state"] = "CLOSED"
    produced["delivery"]["ack"] = "UNKNOWN"
    produced["delivery"]["observed_commit"] = None
    produced["verification"]["verdict"] = "UNKNOWN"
    produced["history"][-1]["to"] = "CLOSED"
    errors = validate_record(produced)
    results.append(("T2_WRITE_NOT_DELIVERY", any(code in errors for code in {"E_OBSERVED_COMMIT_MISMATCH", "E_ACK_REQUIRED", "E_VERIFICATION_NOT_PASS"}), ",".join(errors)))

    home = base_record()
    school = copy.deepcopy(home)
    for record, site, lease_id, token in ((home, "HOME", "L-H", 8), (school, "SCHOOL", "L-S", 9)):
        record["lease"].update({"status": "ACTIVE", "site": site, "lease_id": lease_id, "fencing_token": token, "heartbeat_at": "2026-09-15T09:00:00Z", "expires_at": "2026-09-15T09:05:00Z"})
    lease_errors = validate_peer_leases([home, school])
    results.append(("T4_SCHOOL_HOME_DOUBLE_EXECUTION", "E_DOUBLE_ACTIVE_LEASE:repo:WP001" in lease_errors, ",".join(lease_errors)))

    alarm = base_record()
    alarm["gate"]["alarms"] = [{"alarm_id": "only-alarm", "severity": "CRITICAL", "verdict": "UNKNOWN", "evidence_ref": "alarm.json"}]
    results.append(("T7_SINGLE_CRITICAL_ALARM", effective_gate(alarm) == "BLOCK", effective_gate(alarm)))

    restart = base_record()
    first = validate_record(restart)
    restarted = copy.deepcopy(restart)
    restarted["recovery"]["attempt_id"] = "attempt-3"
    restarted["recovery"]["previous_attempt_id"] = "attempt-2"
    same_key = restarted["idempotency_key"] == restart["idempotency_key"]
    valid_resume = not validate_record(restarted)
    tampered = copy.deepcopy(restarted)
    tampered["artifact"]["content_sha256"] = None
    tamper_blocked = "E_PRODUCED_WITHOUT_CONTENT_SHA" in validate_record(tampered)
    results.append(("T8_RESTART_COMPACTION_RECOVERY", not first and same_key and valid_resume and tamper_blocked, "same_key=%s tamper_blocked=%s" % (same_key, tamper_blocked)))

    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", nargs="?", type=Path)
    parser.add_argument("--peer-state", action="append", default=[], type=Path)
    parser.add_argument("--graph", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    failed = False
    if args.self_test:
        for name, passed, detail in self_test():
            print(f"{name}: {'PASS' if passed else 'FAIL'} | {detail}")
            failed |= not passed
    if args.graph:
        errors = validate_graph(json.loads(args.graph.read_text(encoding="utf-8-sig")))
        print("GRAPH: " + ("PASS" if not errors else "BLOCK | " + ",".join(errors)))
        failed |= bool(errors)
    if args.record:
        records = [json.loads(args.record.read_text(encoding="utf-8-sig"))]
        records.extend(json.loads(path.read_text(encoding="utf-8-sig")) for path in args.peer_state)
        errors = validate_record(records[0]) + validate_peer_leases(records)
        print("RECORD: " + ("PASS" if not errors else "BLOCK | " + ",".join(sorted(set(errors)))))
        failed |= bool(errors)
    if not (args.self_test or args.graph or args.record):
        parser.error("select --self-test, --graph, or a record")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
