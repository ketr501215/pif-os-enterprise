#!/usr/bin/env python3
"""Minimal fail-closed invariant verifier for RayFlow task-state v0.1."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
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
SUCCESS_CODES = {"0", "200", "201", "204"}
MAX_CAPABILITY_AGE = timedelta(hours=24)


def _type_matches(value: object, expected: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }.get(expected, True)


def _resolve_ref(root: dict, ref: str) -> dict:
    if not ref.startswith("#/"):
        raise ValueError("only local JSON Schema refs are supported")
    node: object = root
    for token in ref[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        node = node[token]  # type: ignore[index]
    if not isinstance(node, dict):
        raise ValueError("schema ref did not resolve to an object")
    return node


def validate_json_schema(instance: object, schema: dict, root: dict | None = None, path: str = "$") -> list[str]:
    """Validate the JSON Schema keyword subset used by task-state-v0.1."""
    root = root or schema
    if "$ref" in schema:
        return validate_json_schema(instance, _resolve_ref(root, schema["$ref"]), root, path)
    if "anyOf" in schema:
        if not any(not validate_json_schema(instance, choice, root, path) for choice in schema["anyOf"]):
            return [f"E_JSON_SCHEMA_ANYOF:{path}"]
        return []

    errors: list[str] = []
    expected = schema.get("type")
    if expected:
        types = expected if isinstance(expected, list) else [expected]
        if not any(_type_matches(instance, item) for item in types):
            return [f"E_JSON_SCHEMA_TYPE:{path}"]
    if "const" in schema and instance != schema["const"]:
        errors.append(f"E_JSON_SCHEMA_CONST:{path}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"E_JSON_SCHEMA_ENUM:{path}")
    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"E_JSON_SCHEMA_MIN_LENGTH:{path}")
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(f"E_JSON_SCHEMA_PATTERN:{path}")
        if schema.get("format") == "date-time":
            try:
                parse_time(instance)
            except ValueError:
                errors.append(f"E_JSON_SCHEMA_DATETIME:{path}")
    if isinstance(instance, int) and not isinstance(instance, bool) and "minimum" in schema and instance < schema["minimum"]:
        errors.append(f"E_JSON_SCHEMA_MINIMUM:{path}")
    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"E_JSON_SCHEMA_REQUIRED:{path}.{key}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in properties:
                    errors.append(f"E_JSON_SCHEMA_ADDITIONAL:{path}.{key}")
        for key, child in properties.items():
            if key in instance:
                errors.extend(validate_json_schema(instance[key], child, root, f"{path}.{key}"))
    if isinstance(instance, list) and "items" in schema:
        if len(instance) < schema.get("minItems", 0):
            errors.append(f"E_JSON_SCHEMA_MIN_ITEMS:{path}")
        for index, item in enumerate(instance):
            errors.extend(validate_json_schema(item, schema["items"], root, f"{path}[{index}]"))
    return errors


def state_at_least(state: str, floor: str) -> bool:
    return state in STATE_INDEX and STATE_INDEX[state] >= STATE_INDEX[floor]


def compute_idempotency_key(record: dict) -> str:
    artifact = record.get("artifact", {})
    material = "\n".join([
        str(artifact.get("repository", "")),
        str(record.get("task_id", "")),
        str(record.get("requirement_revision", "")),
        str(artifact.get("path", "")),
        str(artifact.get("branch", "")),
    ])
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def observed_capability_verdict(capability: dict) -> str:
    if capability.get("expected_state") != "READY":
        return "UNKNOWN"
    outcome = capability.get("observed_outcome")
    code = str(capability.get("result_code", ""))
    if outcome == "SUCCESS" and code in SUCCESS_CODES:
        return "PASS"
    if outcome in {"DENIED", "FAILED"} or code in {"401", "403"}:
        return "BLOCK"
    return "UNKNOWN"


def required_publish_capability(record: dict, evaluation_time: datetime | None = None) -> str:
    if not state_at_least(record.get("current_state", ""), "PUBLISHED"):
        return "PASS"
    actor = record.get("actor", {})
    artifact = record.get("artifact", {})
    delivery = record.get("delivery", {})
    matches = [
        cap for cap in record.get("capabilities", [])
        if cap.get("actor_id") == actor.get("agent_id")
        and cap.get("credential_ref") == actor.get("credential_ref")
        and cap.get("machine_id") == actor.get("machine_id")
        and cap.get("site") == actor.get("site")
        and cap.get("repository") == artifact.get("repository")
        and cap.get("ref") == artifact.get("branch")
        and cap.get("operation") == delivery.get("required_publish_operation")
    ]
    if not matches:
        return "UNKNOWN"
    now = evaluation_time or datetime.now(timezone.utc)
    verdicts: list[str] = []
    for capability in matches:
        verdict = observed_capability_verdict(capability)
        try:
            observed_at = parse_time(capability["observed_at"])
            if observed_at > now or now - observed_at > MAX_CAPABILITY_AGE:
                verdict = "UNKNOWN"
        except (AttributeError, KeyError, TypeError, ValueError):
            verdict = "UNKNOWN"
        verdicts.append(verdict)
    if any(verdict == "BLOCK" for verdict in verdicts):
        return "BLOCK"
    if any(verdict == "UNKNOWN" for verdict in verdicts):
        return "UNKNOWN"
    return "PASS"


def effective_gate(record: dict, evaluation_time: datetime | None = None) -> str:
    alarms = record.get("gate", {}).get("alarms", [])
    if any(a.get("verdict") == "BLOCK" for a in alarms):
        return "BLOCK"
    if any(a.get("severity") == "CRITICAL" and a.get("verdict") != "PASS" for a in alarms):
        return "BLOCK"
    if required_publish_capability(record, evaluation_time) != "PASS":
        return "BLOCK"
    if any(a.get("evidence_ref") in {None, ""} for a in alarms):
        return "BLOCK"
    verification = record.get("verification", {})
    if verification.get("verdict") != "PASS" or not verification.get("independent_of_builder", False):
        return "BLOCK"
    if any(a.get("severity") == "NONCRITICAL" and a.get("verdict") == "UNKNOWN" for a in alarms):
        return "UNKNOWN"
    if any(a.get("severity") == "NONCRITICAL" and a.get("verdict") == "DEGRADED" for a in alarms):
        return "DEGRADED"
    return "PASS"


def validate_record(
    record: dict,
    graph: dict | None = None,
    evaluation_time: datetime | None = None,
    evaluation_mode: str = "LIVE",
) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version", "task_id", "work_package_id", "title",
        "requirement_revision", "idempotency_key", "criticality",
        "current_state", "actor", "capabilities", "dependencies", "artifact", "delivery",
        "verification", "gate", "lease", "recovery", "completion_proof", "history", "updated_at",
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
    elif record["idempotency_key"] != compute_idempotency_key(record):
        errors.append("E_IDEMPOTENCY_KEY_MISMATCH")

    state = record["current_state"]
    now = evaluation_time or datetime.now(timezone.utc)
    artifact = record["artifact"]
    delivery = record["delivery"]
    verification = record["verification"]
    lease = record["lease"]

    if state in {"RUNNING", "PRODUCED", "PERSISTED"}:
        if lease.get("status") != "ACTIVE":
            errors.append("E_WRITE_STATE_WITHOUT_ACTIVE_LEASE")
        if not lease.get("lease_id") or lease.get("fencing_token", 0) <= 0:
            errors.append("E_ACTIVE_LEASE_ID_OR_FENCE")
        if lease.get("holder_agent_id") != record["actor"].get("agent_id"):
            errors.append("E_LEASE_HOLDER_MISMATCH")
        if lease.get("machine_id") != record["actor"].get("machine_id"):
            errors.append("E_LEASE_MACHINE_MISMATCH")
        if lease.get("site") != record["actor"].get("site"):
            errors.append("E_LEASE_SITE_MISMATCH")
        try:
            heartbeat = parse_time(lease["heartbeat_at"])
            expires = parse_time(lease["expires_at"])
            updated = parse_time(record["updated_at"])
            if not (heartbeat <= updated <= now < expires):
                errors.append("E_ACTIVE_LEASE_NOT_CURRENT")
        except (AttributeError, KeyError, TypeError, ValueError):
            errors.append("E_ACTIVE_LEASE_TIME_UNKNOWN")

    for capability in record["capabilities"]:
        if capability.get("verdict") != observed_capability_verdict(capability):
            errors.append("E_CAPABILITY_VERDICT_MISMATCH")
    if state_at_least(state, "PUBLISHED") and required_publish_capability(record, now) != "PASS":
        errors.append("E_PUBLISHED_WITHOUT_WRITER_CAPABILITY")

    if state_at_least(state, "PRODUCED") and not HEX64.fullmatch(str(artifact.get("content_sha256") or "")):
        errors.append("E_PRODUCED_WITHOUT_CONTENT_SHA")
    if state_at_least(state, "PUBLISHED") and not HEX40.fullmatch(str(artifact.get("git_commit") or "")):
        errors.append("E_PUBLISHED_WITHOUT_COMMIT")
    if state_at_least(state, "OBSERVED"):
        if delivery.get("expected_commit") != artifact.get("git_commit"):
            errors.append("E_EXPECTED_COMMIT_NOT_ARTIFACT")
        if delivery.get("expected_content_sha256") != artifact.get("content_sha256"):
            errors.append("E_EXPECTED_CONTENT_NOT_ARTIFACT")
        if delivery.get("expected_commit") != delivery.get("observed_commit"):
            errors.append("E_OBSERVED_COMMIT_MISMATCH")
        if delivery.get("expected_content_sha256") != delivery.get("observed_content_sha256"):
            errors.append("E_OBSERVED_CONTENT_MISMATCH")
        if not delivery.get("observer_agent_id") or not delivery.get("observation_method"):
            errors.append("E_OBSERVED_WITHOUT_OBSERVER")
        if delivery.get("observer_agent_id") == record["actor"].get("agent_id"):
            errors.append("E_SELF_ACK_FORBIDDEN")
    if state_at_least(state, "ACKED") and delivery.get("ack") != "YES":
        errors.append("E_ACK_REQUIRED")
    if state_at_least(state, "VERIFIED"):
        if graph is None:
            errors.append("E_DEPENDENCY_GRAPH_REQUIRED")
        else:
            errors.extend(validate_record_graph_binding(record, graph))
        if any(not d.get("satisfied", False) for d in record["dependencies"]):
            errors.append("E_DEPENDENCY_OPEN")
        if verification.get("verdict") != "PASS":
            errors.append("E_VERIFICATION_NOT_PASS")
        if not verification.get("independent_of_builder", False):
            errors.append("E_VERIFIER_NOT_INDEPENDENT")
        if verification.get("verifier_agent_id") == record["actor"].get("agent_id"):
            errors.append("E_SELF_VERIFICATION_FORBIDDEN")
        if verification.get("method_class") == "NONE" or not verification.get("evidence_ref"):
            errors.append("E_VERIFICATION_EVIDENCE_REQUIRED")
        if effective_gate(record, now) != "PASS":
            errors.append("E_GATE_NOT_PASS")
        proof = record["completion_proof"]
        if proof.get("evaluation_mode") != "LIVE":
            errors.append("E_COMPLETION_PROOF_NOT_LIVE")
        try:
            if parse_time(proof["evaluated_at"]) > now:
                errors.append("E_COMPLETION_PROOF_FROM_FUTURE")
        except (AttributeError, KeyError, TypeError, ValueError):
            errors.append("E_COMPLETION_PROOF_TIME_UNKNOWN")
        if not proof.get("artifact_verified_live"):
            errors.append("E_ARTIFACT_NOT_LIVE_VERIFIED")
        for field in ("publication_ref", "ack_ref", "verification_ref", "gate_ref"):
            if not proof.get(field):
                errors.append("E_COMPLETION_PROOF_REF:" + field)
        named_refs = {proof.get(field) for field in ("publication_ref", "ack_ref", "verification_ref", "gate_ref")}
        if not named_refs.issubset(set(proof.get("evidence_refs", []))):
            errors.append("E_COMPLETION_PROOF_EVIDENCE_REFS")
        release_ref = proof.get("lease_release_evidence")
        if lease.get("status") != "RELEASED" or not isinstance(release_ref, dict):
            errors.append("E_VERIFIED_LEASE_NOT_RELEASED")
        elif release_ref.get("path") not in set(proof.get("evidence_refs", [])):
            errors.append("E_LEASE_RELEASE_NOT_IN_EVIDENCE_REFS")
        elif release_ref.get("path") in named_refs:
            errors.append("E_LEASE_RELEASE_NOT_DISTINCT")
        if lease.get("status") == "RELEASED":
            if not lease.get("lease_id") or lease.get("fencing_token", 0) <= 0:
                errors.append("E_RELEASED_LEASE_ID_OR_FENCE")
            if lease.get("holder_agent_id") != record["actor"].get("agent_id"):
                errors.append("E_RELEASED_LEASE_HOLDER_MISMATCH")
            if lease.get("machine_id") != record["actor"].get("machine_id"):
                errors.append("E_RELEASED_LEASE_MACHINE_MISMATCH")
            if lease.get("site") != record["actor"].get("site"):
                errors.append("E_RELEASED_LEASE_SITE_MISMATCH")
            if not lease.get("heartbeat_at") or not lease.get("expires_at"):
                errors.append("E_RELEASED_LEASE_TIME_UNKNOWN")
        if evaluation_mode != "LIVE":
            errors.append("E_HISTORICAL_NOT_LIVE_GATE")
    computed = effective_gate(record, now)
    if record["gate"].get("computed_verdict") != computed:
        errors.append("E_GATE_COMPUTATION_MISMATCH")
    if state == "CLOSED":
        if lease.get("status") not in {"NONE", "RELEASED"}:
            errors.append("E_LEASE_NOT_RELEASED")
        proof = record["completion_proof"]
        ray = proof.get("ray_acceptance")
        if (record["criticality"] == "CRITICAL" or record["work_package_id"].startswith("WP")) and not ray:
            errors.append("E_RAY_ACCEPTANCE_REQUIRED")

    recovery = record["recovery"]
    if recovery.get("previous_attempt_id") is not None:
        if recovery.get("previous_idempotency_key") != record["idempotency_key"]:
            errors.append("E_RECOVERY_IDEMPOTENCY_DRIFT")
        if recovery.get("previous_artifact_content_sha256") != artifact.get("content_sha256"):
            errors.append("E_RECOVERY_ARTIFACT_DRIFT")
    if recovery.get("resume_allowed") and not HEX64.fullmatch(str(recovery.get("context_digest") or "")):
        errors.append("E_RECOVERY_CONTEXT_DIGEST")
    if recovery.get("resume_allowed") and not recovery.get("context_ref"):
        errors.append("E_RECOVERY_CONTEXT_REF")

    resource = str(lease.get("resource", ""))
    if not resource or resource != resource.casefold() or not re.fullmatch(r"[a-z0-9][a-z0-9:/._-]+", resource):
        errors.append("E_LEASE_RESOURCE_NOT_CANONICAL")

    history = record["history"]
    if not history:
        errors.append("E_HISTORY_EMPTY")
    elif history[0].get("from") is not None or history[0].get("to") != "CREATED":
        errors.append("E_HISTORY_ORIGIN")
    if [event.get("sequence") for event in history] != list(range(1, len(history) + 1)):
        errors.append("E_HISTORY_SEQUENCE")
    for previous, current in zip(history, history[1:]):
        if current.get("from") != previous.get("to"):
            errors.append("E_HISTORY_LINK")
            break
        if current.get("from") in STATE_INDEX and current.get("to") in STATE_INDEX and STATE_INDEX[current["to"]] != STATE_INDEX[current["from"]] + 1:
            errors.append("E_HISTORY_NON_ADJACENT")
            break
    if history and history[-1].get("to") != state:
        errors.append("E_HISTORY_HEAD")
    history_states = {event.get("to") for event in history}
    if lease.get("status") == "NONE" and history_states.intersection({"RUNNING", "PRODUCED", "PERSISTED"}):
        errors.append("E_HISTORY_WRITE_WITHOUT_LEASE_EVIDENCE")
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
            if str(left.get("resource", "")).casefold() != str(right.get("resource", "")).casefold():
                continue
            errors.append("E_DOUBLE_ACTIVE_LEASE:" + str(left.get("resource")))
    return errors


def validate_live_artifact(record: dict, repo_root: Path) -> list[str]:
    errors: list[str] = []
    if not state_at_least(record.get("current_state", ""), "PUBLISHED"):
        return errors
    artifact = record["artifact"]
    commit = artifact.get("git_commit")
    branch = artifact.get("branch")
    path = artifact.get("path")
    expected_sha = str(artifact.get("content_sha256") or "").upper()
    try:
        origin_url = subprocess.run(
            ["git", "-C", str(repo_root), "remote", "get-url", "origin"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        def normalized_repo(value: str) -> str:
            normalized = value.strip().replace("git@github.com:", "https://github.com/").rstrip("/")
            return normalized[:-4].lower() if normalized.lower().endswith(".git") else normalized.lower()
        if normalized_repo(str(artifact.get("repository", ""))) != normalized_repo(origin_url):
            errors.append("E_REPOSITORY_ORIGIN_MISMATCH")
        remote = subprocess.run(
            ["git", "-C", str(repo_root), "ls-remote", "--heads", "origin", f"refs/heads/{branch}"],
            check=True, capture_output=True, text=True,
        ).stdout.strip().split()
        if not remote:
            return ["E_LIVE_REMOTE_HEAD_MISSING"]
        remote_head = remote[0]
        ancestor = subprocess.run(
            ["git", "-C", str(repo_root), "merge-base", "--is-ancestor", commit, remote_head],
            capture_output=True,
        )
        if ancestor.returncode != 0:
            errors.append("E_ARTIFACT_COMMIT_NOT_ON_REMOTE_BRANCH")
        content = subprocess.run(
            ["git", "-C", str(repo_root), "show", f"{commit}:{path}"],
            check=True, capture_output=True,
        ).stdout
        observed_sha = hashlib.sha256(content).hexdigest().upper()
        if observed_sha != expected_sha:
            errors.append("E_LIVE_ARTIFACT_SHA_MISMATCH")
    except (OSError, subprocess.CalledProcessError, TypeError) as exc:
        errors.append("E_LIVE_ARTIFACT_UNKNOWN:" + type(exc).__name__)
    return errors


def validate_live_lease_release(record: dict, repo_root: Path) -> list[str]:
    """Resolve and bind a committed lease-release receipt for VERIFIED/CLOSED."""
    if not state_at_least(record.get("current_state", ""), "VERIFIED"):
        return []
    release_ref = record.get("completion_proof", {}).get("lease_release_evidence")
    if not isinstance(release_ref, dict):
        return ["E_LIVE_LEASE_RELEASE_REQUIRED"]

    probe = copy.deepcopy(record)
    probe["artifact"] = release_ref
    live_errors = ["E_LEASE_RELEASE_" + item for item in validate_live_artifact(probe, repo_root)]
    try:
        receipt_bytes = subprocess.run(
            ["git", "-C", str(repo_root), "show", f"{release_ref['git_commit']}:{release_ref['path']}"],
            check=True, capture_output=True,
        ).stdout
        receipt = json.loads(receipt_bytes.decode("utf-8-sig"))
    except (OSError, subprocess.CalledProcessError, KeyError, UnicodeDecodeError, json.JSONDecodeError):
        return live_errors + ["E_LEASE_RELEASE_RECEIPT_UNREADABLE"]

    lease = record["lease"]
    expected = {
        "schema_version": "rayflow.lease-release/v0.1",
        "task_id": record["task_id"],
        "resource": lease.get("resource"),
        "lease_id": lease.get("lease_id"),
        "holder_agent_id": lease.get("holder_agent_id"),
        "machine_id": lease.get("machine_id"),
        "site": lease.get("site"),
        "fencing_token": lease.get("fencing_token"),
        "last_heartbeat_at": lease.get("heartbeat_at"),
        "expires_at": lease.get("expires_at"),
        "status": "RELEASED",
    }
    for field, value in expected.items():
        if receipt.get(field) != value:
            live_errors.append("E_LEASE_RELEASE_BINDING:" + field)
    try:
        acquired = parse_time(receipt["acquired_at"])
        heartbeat = parse_time(receipt["last_heartbeat_at"])
        released = parse_time(receipt["released_at"])
        expires = parse_time(receipt["expires_at"])
        if not (acquired <= heartbeat <= released < expires):
            live_errors.append("E_LEASE_RELEASE_TIME_ORDER")
    except (AttributeError, KeyError, TypeError, ValueError):
        live_errors.append("E_LEASE_RELEASE_TIME_UNKNOWN")
    return live_errors


def validate_recovery_evidence(
    record: dict,
    previous: dict | None,
    previous_bytes: bytes | None,
    context_bytes: bytes | None,
    schema: dict | None = None,
    graph: dict | None = None,
) -> list[str]:
    recovery = record["recovery"]
    if recovery.get("previous_attempt_id") is None:
        return []
    if previous is None or previous_bytes is None:
        return ["E_PREVIOUS_STATE_REQUIRED"]
    errors: list[str] = []
    if schema is not None:
        errors.extend("E_PREVIOUS_" + item for item in validate_json_schema(previous, schema))
    try:
        previous_as_of = parse_time(previous["updated_at"])
    except (AttributeError, KeyError, TypeError, ValueError):
        previous_as_of = datetime.now(timezone.utc)
    errors.extend(
        "E_PREVIOUS_" + item
        for item in validate_record(previous, graph=graph, evaluation_time=previous_as_of)
    )
    if hashlib.sha256(previous_bytes).hexdigest().upper() != str(recovery.get("previous_snapshot_sha256") or "").upper():
        errors.append("E_PREVIOUS_SNAPSHOT_SHA")
    if previous.get("recovery", {}).get("attempt_id") != recovery.get("previous_attempt_id"):
        errors.append("E_PREVIOUS_ATTEMPT_MISMATCH")
    if previous.get("idempotency_key") != record.get("idempotency_key"):
        errors.append("E_PREVIOUS_IDEMPOTENCY_MISMATCH")
    if previous.get("artifact", {}).get("content_sha256") != record.get("artifact", {}).get("content_sha256"):
        errors.append("E_PREVIOUS_ARTIFACT_MISMATCH")
    if previous.get("current_state") != recovery.get("last_durable_state"):
        errors.append("E_PREVIOUS_STATE_MISMATCH")
    if context_bytes is None:
        errors.append("E_CONTEXT_BYTES_REQUIRED")
    elif hashlib.sha256(context_bytes).hexdigest().upper() != str(recovery.get("context_digest") or "").upper():
        errors.append("E_CONTEXT_SHA")
    return errors


def validate_record_graph_binding(record: dict, graph: dict) -> list[str]:
    """Require the task record dependency set to match its declared graph node."""
    nodes = {node.get("task_id"): node for node in graph.get("nodes", [])}
    node = nodes.get(record.get("task_id"))
    if node is None:
        return ["E_TASK_NOT_IN_GRAPH"]

    expected = set(node.get("depends_on", []))
    actual_items = record.get("dependencies", [])
    actual = {item.get("task_id") for item in actual_items}
    errors: list[str] = []
    for task_id in sorted(expected - actual):
        errors.append("E_DEPENDENCY_GRAPH_MISSING:" + str(task_id))
    for task_id in sorted(actual - expected):
        errors.append("E_DEPENDENCY_UNKNOWN_EDGE:" + str(task_id))
    for dependency in actual_items:
        task_id = dependency.get("task_id")
        if task_id not in expected:
            continue
        target = nodes.get(task_id)
        if target is None:
            errors.append("E_DEPENDENCY_GRAPH_TARGET_MISSING:" + str(task_id))
            continue
        required_state = target.get("required_state")
        if dependency.get("required_state") != required_state:
            errors.append("E_DEPENDENCY_REQUIRED_STATE_MISMATCH:" + str(task_id))
        observed_state = dependency.get("observed_state")
        if not (
            observed_state in STATE_INDEX
            and required_state in STATE_INDEX
            and STATE_INDEX[observed_state] >= STATE_INDEX[required_state]
        ):
            errors.append("E_DEPENDENCY_STATE_UNSATISFIED:" + str(task_id))
        if dependency.get("satisfied") is not True or not dependency.get("evidence_ref"):
            errors.append("E_DEPENDENCY_EVIDENCE_UNSATISFIED:" + str(task_id))
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


def base_graph() -> dict:
    return {
        "schema_version": "rayflow.dependency-graph/v0.1",
        "work_package_id": "WP001",
        "nodes": [
            {
                "task_id": "WP001_WORKFLOW_GATE",
                "required_state": "OBSERVED",
                "depends_on": [],
            },
            {
                "task_id": "WP001-SCHEMA",
                "required_state": "VERIFIED",
                "depends_on": ["WP001_WORKFLOW_GATE"],
            },
        ],
    }


def base_record() -> dict:
    digest = hashlib.sha256(b"repo\nWP001-SCHEMA\nv0.1\n04_KNOWLEDGE_OS/SCHEMA_v0.1.md\nmain").hexdigest()
    now_text = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "schema_version": "rayflow.task-state/v0.1",
        "task_id": "WP001-SCHEMA",
        "work_package_id": "WP001",
        "title": "Knowledge OS schema",
        "requirement_revision": "v0.1",
        "idempotency_key": digest,
        "criticality": "CRITICAL",
        "current_state": "VERIFIED",
        "actor": {"agent_id": "CODEX", "credential_ref": "credential:test", "role": "BUILDER", "vendor": "OpenAI", "machine_id": "HOME-1", "site": "HOME", "session_id": "test"},
        "capabilities": [
            {"actor_id": "CODEX", "credential_ref": "credential:test", "machine_id": "HOME-1", "site": "HOME", "repository": "repo", "ref": "main", "operation": "READ", "expected_state": "READY", "live_observation": "git fetch succeeded", "observed_outcome": "SUCCESS", "result_code": "0", "observed_at": now_text, "evidence_ref": "read.json", "verdict": "PASS"},
            {"actor_id": "CODEX", "credential_ref": "credential:test", "machine_id": "HOME-1", "site": "HOME", "repository": "repo", "ref": "main", "operation": "PUSH", "expected_state": "READY", "live_observation": "git push succeeded", "observed_outcome": "SUCCESS", "result_code": "0", "observed_at": now_text, "evidence_ref": "push.json", "verdict": "PASS"}
        ],
        "dependencies": [{"task_id": "WP001_WORKFLOW_GATE", "required_state": "OBSERVED", "observed_state": "OBSERVED", "satisfied": True, "evidence_ref": "review.json"}],
        "artifact": {"repository": "repo", "branch": "main", "path": "04_KNOWLEDGE_OS/SCHEMA_v0.1.md", "content_sha256": "a" * 64, "git_commit": "b" * 40},
        "delivery": {"required_publish_operation": "PUSH", "expected_commit": "b" * 40, "observed_commit": "b" * 40, "expected_content_sha256": "a" * 64, "observed_content_sha256": "a" * 64, "observer_agent_id": "CLAUDE", "observation_method": "git-show-and-hash", "ack": "YES"},
        "verification": {"verifier_agent_id": "ADVERSARY", "method_class": "ADVERSARIAL_TEST", "independent_of_builder": True, "verdict": "PASS", "evidence_ref": "verification.json"},
        "gate": {"declared_verdict": "PASS", "computed_verdict": "PASS", "alarms": []},
        "lease": {"resource": "repo:wp001", "lease_id": "lease-test", "holder_agent_id": "CODEX", "machine_id": "HOME-1", "site": "HOME", "fencing_token": 2, "heartbeat_at": now_text, "expires_at": "2099-01-01T00:00:00Z", "status": "RELEASED"},
        "recovery": {"attempt_id": "attempt-1", "previous_attempt_id": None, "previous_idempotency_key": None, "previous_artifact_content_sha256": None, "previous_snapshot_ref": None, "previous_snapshot_sha256": None, "last_durable_state": "VERIFIED", "context_ref": None, "context_digest": None, "resume_allowed": False},
        "completion_proof": {"proof_id": "proof-test", "evaluation_mode": "LIVE", "evaluated_at": now_text, "artifact_verified_live": True, "publication_ref": "publication.json", "ack_ref": "ack.json", "verification_ref": "verification.json", "gate_ref": "gate.json", "evidence_refs": ["publication.json", "ack.json", "verification.json", "gate.json", "lease.json"], "lease_release_evidence": {"repository": "repo", "branch": "main", "path": "lease.json", "content_sha256": "c" * 64, "git_commit": "d" * 40}, "ray_acceptance": None},
        "history": [
            {"sequence": i + 1, "from": STATES[i - 1] if i else None, "to": state, "at": now_text, "evidence_ref": f"evidence-{i + 1}"}
            for i, state in enumerate(STATES[:10])
        ],
        "updated_at": now_text
    }


def self_test() -> list[tuple[str, bool, str]]:
    results: list[tuple[str, bool, str]] = []
    graph = base_graph()

    def check(record: dict, mode: str = "LIVE") -> list[str]:
        return validate_record(record, graph=graph, evaluation_mode=mode)

    schema_path = Path(__file__).resolve().parent.parent / "SCHEMA" / "task-state-v0.1.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8-sig"))
    schema_errors = validate_json_schema(base_record(), schema)
    results.append(("SCHEMA_RUNTIME_VALIDATION", not schema_errors, ",".join(schema_errors)))

    permission_split = base_record()
    permission_split["capabilities"] = [
        {"actor_id": "CODEX", "credential_ref": "credential:test", "machine_id": "HOME-1", "site": "HOME", "repository": "repo", "ref": "main", "operation": "READ", "expected_state": "READY", "live_observation": "read succeeded", "observed_outcome": "SUCCESS", "result_code": "0", "observed_at": "2026-09-15T00:00:00+08:00", "evidence_ref": "read.json", "verdict": "PASS"},
        {"actor_id": "CODEX", "credential_ref": "credential:test", "machine_id": "HOME-1", "site": "HOME", "repository": "repo", "ref": "main", "operation": "PUSH", "expected_state": "READY", "live_observation": "older push succeeded", "observed_outcome": "SUCCESS", "result_code": "0", "observed_at": "2026-09-15T00:00:00+08:00", "evidence_ref": "old-push.json", "verdict": "PASS"},
        {"actor_id": "CODEX", "credential_ref": "credential:test", "machine_id": "HOME-1", "site": "HOME", "repository": "repo", "ref": "main", "operation": "PUSH", "expected_state": "READY", "live_observation": "HTTP 403", "observed_outcome": "DENIED", "result_code": "403", "observed_at": "2026-09-15T00:00:01+08:00", "evidence_ref": "write-403.json", "verdict": "BLOCK"}
    ]
    permission_errors = check(permission_split)
    results.append(("I1_READ_READY_WRITE_FAIL", "E_PUBLISHED_WITHOUT_WRITER_CAPABILITY" in permission_errors, ",".join(permission_errors)))

    forged_capability = base_record()
    forged_capability["capabilities"][1].update({"observed_outcome": "DENIED", "result_code": "403", "live_observation": "HTTP 403", "verdict": "PASS"})
    forged_errors = check(forged_capability)
    results.append(("I1_CLAIMED_PASS_WITH_403", "E_CAPABILITY_VERDICT_MISMATCH" in forged_errors and "E_PUBLISHED_WITHOUT_WRITER_CAPABILITY" in forged_errors, ",".join(forged_errors)))

    stale_capability = base_record()
    stale_capability["capabilities"][1]["observed_at"] = "2020-01-01T00:00:00Z"
    stale_errors = check(stale_capability)
    results.append(("I1_STALE_WRITE_PASS_IS_UNKNOWN", "E_PUBLISHED_WITHOUT_WRITER_CAPABILITY" in stale_errors, ",".join(stale_errors)))

    produced = base_record()
    produced["current_state"] = "CLOSED"
    produced["delivery"]["ack"] = "UNKNOWN"
    produced["delivery"]["observed_commit"] = None
    produced["verification"]["verdict"] = "UNKNOWN"
    produced["history"][-1]["to"] = "CLOSED"
    errors = check(produced)
    results.append(("T2_WRITE_NOT_DELIVERY", any(code in errors for code in {"E_OBSERVED_COMMIT_MISMATCH", "E_ACK_REQUIRED", "E_VERIFICATION_NOT_PASS"}), ",".join(errors)))

    home = base_record()
    school = copy.deepcopy(home)
    for record, site, lease_id, token in ((home, "HOME", "L-H", 8), (school, "SCHOOL", "L-S", 9)):
        record["lease"].update({"status": "ACTIVE", "site": site, "lease_id": lease_id, "fencing_token": token, "heartbeat_at": "2026-09-15T09:00:00Z", "expires_at": "2026-09-15T09:05:00Z"})
    lease_errors = validate_peer_leases([home, school])
    results.append(("T4_SCHOOL_HOME_DOUBLE_EXECUTION", "E_DOUBLE_ACTIVE_LEASE:repo:wp001" in lease_errors, ",".join(lease_errors)))

    running_without_lease = base_record()
    running_without_lease["current_state"] = "RUNNING"
    running_without_lease["history"] = running_without_lease["history"][:4]
    running_errors = check(running_without_lease)
    results.append(("T4_RUNNING_REQUIRES_ACTIVE_LEASE", "E_WRITE_STATE_WITHOUT_ACTIVE_LEASE" in running_errors, ",".join(running_errors)))

    expired_lease = copy.deepcopy(running_without_lease)
    expired_lease["lease"].update({"status": "ACTIVE", "lease_id": "expired", "holder_agent_id": "CODEX", "machine_id": "HOME-1", "site": "HOME", "fencing_token": 3, "heartbeat_at": "2020-01-01T00:00:00Z", "expires_at": "2020-01-01T00:05:00Z"})
    expired_lease["updated_at"] = "2020-01-01T00:01:00Z"
    expired_errors = check(expired_lease)
    results.append(("T4_EXPIRED_LEASE_BLOCKS", "E_ACTIVE_LEASE_NOT_CURRENT" in expired_errors, ",".join(expired_errors)))

    bootstrap_without_lease = base_record()
    bootstrap_without_lease["lease"].update({"status": "NONE", "fencing_token": 0})
    bootstrap_without_lease["completion_proof"]["lease_release_evidence"] = None
    bootstrap_errors = check(bootstrap_without_lease)
    results.append((
        "T4_BOOTSTRAP_WITHOUT_LEASE_BLOCKS",
        "E_VERIFIED_LEASE_NOT_RELEASED" in bootstrap_errors and "E_HISTORY_WRITE_WITHOUT_LEASE_EVIDENCE" in bootstrap_errors,
        ",".join(bootstrap_errors),
    ))

    alarm = base_record()
    alarm["gate"]["alarms"] = [{"alarm_id": "only-alarm", "severity": "CRITICAL", "verdict": "UNKNOWN", "evidence_ref": "alarm.json"}]
    results.append(("T7_SINGLE_CRITICAL_ALARM", effective_gate(alarm) == "BLOCK", effective_gate(alarm)))

    degraded_alarm = base_record()
    degraded_alarm["gate"]["alarms"] = [{"alarm_id": "only-alarm", "severity": "CRITICAL", "verdict": "DEGRADED", "evidence_ref": "alarm.json"}]
    results.append(("T7_CRITICAL_DEGRADED_BLOCKS", effective_gate(degraded_alarm) == "BLOCK", effective_gate(degraded_alarm)))

    noncritical_block = base_record()
    noncritical_block["gate"]["alarms"] = [{"alarm_id": "only-alarm", "severity": "NONCRITICAL", "verdict": "BLOCK", "evidence_ref": "alarm.json"}]
    results.append(("T7_NONCRITICAL_BLOCK_IS_NOT_IGNORED", effective_gate(noncritical_block) == "BLOCK", effective_gate(noncritical_block)))

    self_ack = base_record()
    self_ack["delivery"]["observer_agent_id"] = "CODEX"
    self_ack_errors = check(self_ack)
    results.append(("T2_SELF_ACK_FORBIDDEN", "E_SELF_ACK_FORBIDDEN" in self_ack_errors, ",".join(self_ack_errors)))

    bad_history = base_record()
    bad_history["history"] = []
    bad_history_errors = check(bad_history)
    results.append(("T8_EMPTY_HISTORY_BLOCKS", "E_HISTORY_EMPTY" in bad_history_errors, ",".join(bad_history_errors)))

    omitted_dependencies = base_record()
    omitted_dependencies["dependencies"] = []
    omitted_errors = check(omitted_dependencies)
    results.append(("DEPENDENCY_GRAPH_BINDING", "E_DEPENDENCY_GRAPH_MISSING:WP001_WORKFLOW_GATE" in omitted_errors, ",".join(omitted_errors)))

    previous = base_record()
    previous["current_state"] = "ACKED"
    previous["history"] = previous["history"][:9]
    previous["recovery"]["last_durable_state"] = "ACKED"
    previous_bytes = json.dumps(previous, sort_keys=True, separators=(",", ":")).encode("utf-8")
    context_bytes = b"canonical recovery context"
    restarted = base_record()
    restarted["recovery"] = {
        "attempt_id": "attempt-2",
        "previous_attempt_id": "attempt-1",
        "previous_idempotency_key": previous["idempotency_key"],
        "previous_artifact_content_sha256": previous["artifact"]["content_sha256"],
        "previous_snapshot_ref": "previous.json",
        "previous_snapshot_sha256": hashlib.sha256(previous_bytes).hexdigest(),
        "last_durable_state": "ACKED",
        "context_ref": "context.md",
        "context_digest": hashlib.sha256(context_bytes).hexdigest(),
        "resume_allowed": True,
    }
    first = validate_record(previous)
    same_key = restarted["idempotency_key"] == previous["idempotency_key"]
    valid_resume = not check(restarted) and not validate_recovery_evidence(restarted, previous, previous_bytes, context_bytes, schema, graph)
    tampered = copy.deepcopy(restarted)
    tampered["artifact"]["content_sha256"] = "d" * 64
    tamper_blocked = "E_RECOVERY_ARTIFACT_DRIFT" in check(tampered) or "E_PREVIOUS_ARTIFACT_MISMATCH" in validate_recovery_evidence(tampered, previous, previous_bytes, context_bytes, schema, graph)
    changed_key = copy.deepcopy(restarted)
    changed_key["idempotency_key"] = "e" * 64
    key_blocked = "E_IDEMPOTENCY_KEY_MISMATCH" in check(changed_key) or "E_PREVIOUS_IDEMPOTENCY_MISMATCH" in validate_recovery_evidence(changed_key, previous, previous_bytes, context_bytes, schema, graph)
    missing_context = copy.deepcopy(restarted)
    missing_context["recovery"]["context_digest"] = None
    context_blocked = "E_RECOVERY_CONTEXT_DIGEST" in check(missing_context) or "E_CONTEXT_SHA" in validate_recovery_evidence(missing_context, previous, previous_bytes, context_bytes, schema, graph)
    results.append(("T8_RESTART_COMPACTION_RECOVERY", not first and same_key and valid_resume and tamper_blocked and key_blocked and context_blocked, "same_key=%s artifact_blocked=%s key_blocked=%s context_blocked=%s" % (same_key, tamper_blocked, key_blocked, context_blocked)))

    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", nargs="?", type=Path)
    parser.add_argument("--peer-state", action="append", default=[], type=Path)
    parser.add_argument("--graph", type=Path)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--previous-state", type=Path)
    parser.add_argument("--as-of", help="forensic replay timestamp; never valid for a live VERIFIED/CLOSED gate")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    failed = False
    if args.self_test:
        for name, passed, detail in self_test():
            print(f"{name}: {'PASS' if passed else 'FAIL'} | {detail}")
            failed |= not passed
    graph = json.loads(args.graph.read_text(encoding="utf-8-sig")) if args.graph else None
    if graph is not None:
        errors = validate_graph(graph)
        print("GRAPH: " + ("PASS" if not errors else "BLOCK | " + ",".join(errors)))
        failed |= bool(errors)
    if args.record:
        records = [json.loads(args.record.read_text(encoding="utf-8-sig"))]
        records.extend(json.loads(path.read_text(encoding="utf-8-sig")) for path in args.peer_state)
        schema_path = Path(__file__).resolve().parent.parent / "SCHEMA" / "task-state-v0.1.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8-sig"))
        evaluation_mode = "HISTORICAL" if args.as_of else "LIVE"
        try:
            evaluation_time = parse_time(args.as_of) if args.as_of else datetime.now(timezone.utc)
        except (AttributeError, TypeError, ValueError):
            errors = ["E_AS_OF_INVALID"]
            evaluation_time = datetime.now(timezone.utc)
        else:
            errors = []
        errors += validate_json_schema(records[0], schema)
        errors += validate_record(records[0], graph=graph, evaluation_time=evaluation_time, evaluation_mode=evaluation_mode)
        errors += validate_peer_leases(records)
        if evaluation_mode == "LIVE" and state_at_least(records[0].get("current_state", ""), "PUBLISHED"):
            if args.repo_root is None:
                errors.append("E_LIVE_REPO_REQUIRED")
            else:
                errors.extend(validate_live_artifact(records[0], args.repo_root.resolve()))
                errors.extend(validate_live_lease_release(records[0], args.repo_root.resolve()))
        recovery = records[0].get("recovery", {})
        if recovery.get("previous_attempt_id") is not None:
            if args.previous_state is None:
                errors.append("E_PREVIOUS_STATE_REQUIRED")
            else:
                previous_bytes = args.previous_state.read_bytes()
                previous = json.loads(previous_bytes.decode("utf-8-sig"))
                context_bytes = None
                if args.repo_root is not None and recovery.get("context_ref"):
                    context_path = (args.repo_root.resolve() / recovery["context_ref"]).resolve()
                    try:
                        context_path.relative_to(args.repo_root.resolve())
                        context_bytes = context_path.read_bytes()
                    except (ValueError, OSError):
                        errors.append("E_CONTEXT_REF_INVALID")
                errors.extend(validate_recovery_evidence(records[0], previous, previous_bytes, context_bytes, schema, graph))
        label = "RECORD" if evaluation_mode == "LIVE" else f"RECORD (HISTORICAL, as-of={args.as_of}; NOT VALID FOR LIVE GATE)"
        print(label + ": " + ("PASS" if not errors else "BLOCK | " + ",".join(sorted(set(errors)))))
        failed |= bool(errors)
    if not (args.self_test or args.graph or args.record):
        parser.error("select --self-test, --graph, or a record")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
