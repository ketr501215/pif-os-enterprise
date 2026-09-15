#!/usr/bin/env python3
"""Fail-closed verifier for RayFlow role-gate policy and gate-run records."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any


STATES = [
    "CREATED", "DISPATCHED", "ACCEPTED", "RUNNING", "PRODUCED",
    "PERSISTED", "PUBLISHED", "OBSERVED", "ACKED", "VERIFIED", "CLOSED",
]
ROLES = {"HUMAN", "LEAD", "ORCHESTRATOR", "PLANNER", "BUILDER", "VERIFIER", "ADVERSARY"}
VERDICTS = {"PASS", "BLOCK", "DEGRADED", "UNKNOWN"}
HEX64 = re.compile(r"^[a-fA-F0-9]{64}$")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def resolve_repo_file(repo_root: Path, ref: str) -> Path | None:
    try:
        path = (repo_root / ref).resolve()
        path.relative_to(repo_root.resolve())
    except (OSError, ValueError):
        return None
    return path


def adjacent_transitions() -> list[str]:
    return [f"{left}->{right}" for left, right in zip(STATES, STATES[1:])]


def validate_policy(policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if policy.get("schema_version") != "rayflow.role-gates/v0.1":
        errors.append("E_POLICY_SCHEMA")
    if policy.get("policy_id") != "RAYFLOW-ROLE-GATES-001":
        errors.append("E_POLICY_ID")
    if policy.get("status") != "ACTIVE":
        errors.append("E_POLICY_NOT_ACTIVE")
    if policy.get("state_order") != STATES:
        errors.append("E_POLICY_STATE_ORDER")

    roles = policy.get("roles")
    if not isinstance(roles, dict) or set(roles) != ROLES:
        errors.append("E_POLICY_ROLES")
    else:
        for role, spec in roles.items():
            gates = spec.get("gate_catalog") if isinstance(spec, dict) else None
            if not isinstance(gates, list) or not gates or len(gates) != len(set(gates)):
                errors.append(f"E_POLICY_ROLE_GATES:{role}")

    universal = policy.get("universal_gates")
    if not isinstance(universal, list) or not universal or len(universal) != len(set(universal)):
        errors.append("E_POLICY_UNIVERSAL_GATES")

    expected_transitions = set(adjacent_transitions())
    owners = policy.get("transition_owners")
    transition_gates = policy.get("transition_gates")
    if not isinstance(owners, dict) or set(owners) != expected_transitions:
        errors.append("E_POLICY_TRANSITION_OWNERS")
    else:
        for transition, allowed in owners.items():
            if not isinstance(allowed, list) or not allowed or not set(allowed) <= ROLES:
                errors.append(f"E_POLICY_TRANSITION_OWNER:{transition}")
    if not isinstance(transition_gates, dict) or set(transition_gates) != expected_transitions:
        errors.append("E_POLICY_TRANSITION_GATES")
    else:
        for transition, gates in transition_gates.items():
            if not isinstance(gates, list) or not gates or len(gates) != len(set(gates)):
                errors.append(f"E_POLICY_TRANSITION_GATE:{transition}")

    defaults = policy.get("instance_defaults")
    expected_instances = {"Ray", "Lead Agent", "Subagent", "Claude Code", "Codex", "Gemini CLI", "Antigravity CLI"}
    if not isinstance(defaults, dict) or not expected_instances <= set(defaults):
        errors.append("E_POLICY_INSTANCE_DEFAULTS")

    rules = policy.get("verdict_rules")
    if not isinstance(rules, dict) or rules.get("votes_are_inputs") is not False:
        errors.append("E_POLICY_VOTE_RULE")
    assignment_policy = policy.get("role_assignment")
    if (
        not isinstance(assignment_policy, dict)
        or assignment_policy.get("self_declared_role_is_sufficient") is not False
        or assignment_policy.get("physical_sha_readback_required") is not True
        or assignment_policy.get("authority_evidence_physical_sha_required") is not True
    ):
        errors.append("E_POLICY_ROLE_ASSIGNMENT_RULE")
    evidence_policy = policy.get("evidence_policy")
    if not isinstance(evidence_policy, dict) or not all(value is True for value in evidence_policy.values()):
        errors.append("E_POLICY_EVIDENCE_RULE")
    invariants = set(policy.get("hard_invariants", []))
    for required in {
        "A_WRITE_IS_NOT_A_DELIVERY",
        "NO_BUILDER_SELF_ACK_OR_SELF_VERIFICATION",
        "CRITICAL_UNKNOWN_BLOCKS",
        "ONE_ACTIVE_LEASE_PER_RESOURCE_ACROSS_SITES",
        "CONTEXT_SUMMARY_IS_NOT_AUTHORITY",
    }:
        if required not in invariants:
            errors.append(f"E_POLICY_INVARIANT:{required}")
    return errors


def identity_errors(identity: Any, prefix: str) -> list[str]:
    if not isinstance(identity, dict):
        return [f"E_{prefix}_IDENTITY"]
    errors: list[str] = []
    for field in ("agent_id", "role", "vendor", "credential_ref", "session_id", "machine_id", "site"):
        if not isinstance(identity.get(field), str) or not identity[field]:
            errors.append(f"E_{prefix}_{field.upper()}")
    if identity.get("role") not in ROLES:
        errors.append(f"E_{prefix}_ROLE")
    return errors


def validate_assignment(
    assignment: dict[str, Any],
    assignment_bytes: bytes,
    assignment_path: Path,
    record: dict[str, Any],
    policy: dict[str, Any],
    repo_root: Path,
) -> list[str]:
    errors: list[str] = []
    if assignment.get("schema_version") != policy.get("role_assignment", {}).get("schema"):
        errors.append("E_ASSIGNMENT_SCHEMA")
    for field in ("task_id", "attempt_id", "requirement_revision", "idempotency_key"):
        if assignment.get(field) != record.get(field):
            errors.append(f"E_ASSIGNMENT_{field.upper()}_MISMATCH")
    errors.extend(identity_errors(assignment.get("assignee"), "ASSIGNEE"))
    errors.extend(identity_errors(assignment.get("assigned_by"), "ASSIGNER"))
    if assignment.get("assignee") != record.get("actor"):
        errors.append("E_ASSIGNMENT_ACTOR_MISMATCH")
    if assignment.get("assigned_role") != record.get("actor", {}).get("role"):
        errors.append("E_ASSIGNMENT_ROLE_MISMATCH")
    issuer_roles = set(policy.get("role_assignment", {}).get("issuer_roles", []))
    assigner = assignment.get("assigned_by", {})
    if assigner.get("role") not in issuer_roles:
        errors.append("E_ASSIGNMENT_ISSUER_ROLE")
    actor = record.get("actor", {})
    if actor.get("role") != "HUMAN":
        for field in policy.get("identity_dimensions", []):
            if assigner.get(field) == actor.get(field):
                errors.append(f"E_ASSIGNMENT_SELF_ISSUED_{field.upper()}")

    expected_ref = record.get("role_assignment_ref")
    expected_sha = record.get("role_assignment_sha256")
    try:
        actual_ref = assignment_path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        errors.append("E_ASSIGNMENT_OUTSIDE_REPO")
    else:
        if expected_ref != actual_ref:
            errors.append("E_ASSIGNMENT_REF_MISMATCH")
    if not isinstance(expected_sha, str) or sha256_bytes(assignment_bytes) != expected_sha.upper():
        errors.append("E_ASSIGNMENT_SHA_MISMATCH")

    authority = assignment.get("authority_evidence")
    if not isinstance(authority, dict):
        errors.append("E_ASSIGNMENT_AUTHORITY_EVIDENCE")
    else:
        ref = authority.get("ref")
        expected = authority.get("sha256")
        method = authority.get("method")
        evidence_path = resolve_repo_file(repo_root, ref) if isinstance(ref, str) else None
        if evidence_path is None or not evidence_path.is_file():
            errors.append("E_ASSIGNMENT_AUTHORITY_MISSING")
        elif not isinstance(expected, str) or sha256_bytes(evidence_path.read_bytes()) != expected.upper():
            errors.append("E_ASSIGNMENT_AUTHORITY_SHA")
        if method not in {"USER_SESSION_AUTHORITY_RECEIPT", "SIGNED_COMMIT", "EXTERNAL_ATTESTATION", "RAY_DECISION_RECORD"}:
            errors.append("E_ASSIGNMENT_AUTHORITY_METHOD")
    return errors


def compute_check(check: dict[str, Any]) -> str:
    comparison = check.get("comparison")
    if comparison == "MATCH":
        return "PASS" if check.get("expected") == check.get("observed") else "BLOCK"
    if comparison == "MISMATCH":
        return "BLOCK"
    if comparison in {"MISSING", "STALE", "NOT_RUN"}:
        return "UNKNOWN"
    if comparison == "DEGRADED":
        return "DEGRADED"
    return "UNKNOWN"


def compute_gate(checks: list[dict[str, Any]], missing: set[str]) -> str:
    if missing:
        return "BLOCK"
    for check in checks:
        if check.get("critical") is True and check.get("verdict") != "PASS":
            return "BLOCK"
    for check in checks:
        if check.get("verdict") in {"BLOCK", "UNKNOWN"}:
            return "BLOCK"
    if any(check.get("verdict") == "DEGRADED" for check in checks):
        return "DEGRADED"
    return "PASS"


def validate_gate_run(
    record: dict[str, Any],
    policy: dict[str, Any],
    assignment: dict[str, Any],
    assignment_bytes: bytes,
    assignment_path: Path,
    repo_root: Path,
) -> tuple[list[str], str, set[str]]:
    errors: list[str] = []
    if record.get("schema_version") != "rayflow.gate-run/v0.1":
        errors.append("E_GATE_RUN_SCHEMA")
    if record.get("policy_id") != policy.get("policy_id"):
        errors.append("E_GATE_RUN_POLICY")
    for field in ("task_id", "attempt_id", "requirement_revision"):
        if not isinstance(record.get(field), str) or not record[field]:
            errors.append(f"E_GATE_RUN_{field.upper()}")
    if not isinstance(record.get("idempotency_key"), str) or not re.fullmatch(r"[a-f0-9]{64}", record["idempotency_key"]):
        errors.append("E_GATE_RUN_IDEMPOTENCY_KEY")

    actor = record.get("actor")
    errors.extend(identity_errors(actor, "ACTOR"))
    errors.extend(validate_assignment(assignment, assignment_bytes, assignment_path, record, policy, repo_root))
    role = actor.get("role") if isinstance(actor, dict) else None
    current = record.get("current_state")
    target = record.get("target_state")
    transition = f"{current}->{target}"
    if transition not in adjacent_transitions():
        errors.append("E_NON_ADJACENT_TRANSITION")
    allowed = policy.get("transition_owners", {}).get(transition, [])
    if role not in allowed:
        errors.append(f"E_ROLE_NOT_OWNER:{role}:{transition}")

    evidence = record.get("evidence_inputs")
    evidence_refs: set[str] = set()
    if not isinstance(evidence, list) or not evidence:
        errors.append("E_EVIDENCE_INPUTS")
    else:
        for index, item in enumerate(evidence):
            if not isinstance(item, dict) or not isinstance(item.get("ref"), str) or not item["ref"]:
                errors.append(f"E_EVIDENCE_REF:{index}")
                continue
            ref = item["ref"]
            evidence_refs.add(ref)
            if not isinstance(item.get("sha256"), str) or not HEX64.fullmatch(item["sha256"]):
                errors.append(f"E_EVIDENCE_SHA:{index}")
                continue
            evidence_path = resolve_repo_file(repo_root, ref)
            if evidence_path is None or not evidence_path.is_file():
                errors.append(f"E_EVIDENCE_MISSING:{ref}")
            elif sha256_bytes(evidence_path.read_bytes()) != item["sha256"].upper():
                errors.append(f"E_EVIDENCE_SHA_MISMATCH:{ref}")

    checks = record.get("checks")
    valid_checks: list[dict[str, Any]] = []
    if not isinstance(checks, list) or not checks:
        errors.append("E_CHECKS")
    else:
        seen: set[str] = set()
        for index, check in enumerate(checks):
            if not isinstance(check, dict):
                errors.append(f"E_CHECK:{index}")
                continue
            gate_id = check.get("gate_id")
            if not isinstance(gate_id, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]+", gate_id):
                errors.append(f"E_GATE_ID:{index}")
                continue
            if gate_id in seen:
                errors.append(f"E_DUPLICATE_GATE:{gate_id}")
            seen.add(gate_id)
            if check.get("verdict") not in VERDICTS:
                errors.append(f"E_GATE_VERDICT:{gate_id}")
            if not isinstance(check.get("critical"), bool):
                errors.append(f"E_GATE_CRITICAL:{gate_id}")
            for field in ("expected", "observed", "comparison", "evidence_ref"):
                if not isinstance(check.get(field), str) or not check[field]:
                    errors.append(f"E_GATE_{field.upper()}:{gate_id}")
            if check.get("comparison") not in {"MATCH", "MISMATCH", "MISSING", "STALE", "NOT_RUN", "DEGRADED"}:
                errors.append(f"E_GATE_COMPARISON_CODE:{gate_id}")
            if isinstance(check.get("evidence_ref"), str) and check["evidence_ref"] not in evidence_refs:
                errors.append(f"E_GATE_EVIDENCE_NOT_BOUND:{gate_id}")
            computed_check = copy.deepcopy(check)
            computed_check["verdict"] = compute_check(check)
            if check.get("verdict") != computed_check["verdict"]:
                errors.append(f"E_CHECK_VERDICT_MISMATCH:{gate_id}:{check.get('verdict')}:{computed_check['verdict']}")
            valid_checks.append(computed_check)

    required = set(policy.get("universal_gates", []))
    required.update(policy.get("transition_gates", {}).get(transition, []))
    present = {check.get("gate_id") for check in valid_checks}
    missing = required - present

    independence_required = (
        role in set(policy.get("independence_required_roles", []))
        or transition in set(policy.get("independence_required_transitions", []))
    )
    if independence_required:
        builder = record.get("subject_builder")
        errors.extend(identity_errors(builder, "BUILDER"))
        if isinstance(actor, dict) and isinstance(builder, dict):
            for field in policy.get("identity_dimensions", []):
                if actor.get(field) == builder.get(field):
                    errors.append(f"E_INDEPENDENCE_{field.upper()}_MATCH")

    computed = compute_gate(valid_checks, missing)
    if errors:
        computed = "BLOCK"
    if record.get("declared_effective_verdict") != computed:
        errors.append(f"E_DECLARED_VERDICT_MISMATCH:{record.get('declared_effective_verdict')}:{computed}")
    expected_result = target if computed == "PASS" else current
    if record.get("resulting_state") != expected_result:
        errors.append(f"E_RESULTING_STATE:{record.get('resulting_state')}:{expected_result}")
    try:
        datetime.fromisoformat(str(record.get("created_at", "")).replace("Z", "+00:00"))
    except ValueError:
        errors.append("E_CREATED_AT")
    return sorted(set(errors)), computed, missing


def identity(agent: str, role: str, credential: str, session: str) -> dict[str, str]:
    return {
        "agent_id": agent,
        "role": role,
        "vendor": agent.split(":", 1)[0],
        "credential_ref": credential,
        "session_id": session,
        "machine_id": "HOME-1",
        "site": "HOME",
    }


def valid_transition_run(
    policy: dict[str, Any], transition: str, repo_root: Path
) -> tuple[dict[str, Any], dict[str, Any], bytes, Path]:
    current, target = transition.split("->")
    role = policy["transition_owners"][transition][0]
    slug = transition.lower().replace("->", "-to-")
    attempt_id = f"attempt-{slug}"
    actor = identity(f"AGENT:{role}", role, f"cred-{role.lower()}", f"session-{role.lower()}")
    authority_ref = "authority/ray-decision.txt"
    authority_path = repo_root / authority_ref
    authority_path.parent.mkdir(parents=True, exist_ok=True)
    authority_path.write_bytes(b"Ray decision D010")
    evidence_ref = f"evidence/{slug}.json"
    evidence_path = repo_root / evidence_ref
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_bytes = json.dumps({"transition": transition, "observation": "PASS"}, sort_keys=True).encode("utf-8")
    evidence_path.write_bytes(evidence_bytes)
    required = set(policy["universal_gates"])
    required.update(policy["transition_gates"][transition])
    checks = [
        {
            "gate_id": gate_id,
            "critical": gate_id in {"OBSERVER_PROVENANCE", "OBSERVE_EXACT_ARTIFACT", "CRITICAL_ALARM_SCAN"},
            "expected": "PASS",
            "observed": "PASS",
            "comparison": "MATCH",
            "verdict": "PASS",
            "evidence_ref": evidence_ref,
        }
        for gate_id in sorted(required)
    ]
    record = {
        "schema_version": "rayflow.gate-run/v0.1",
        "policy_id": policy["policy_id"],
        "task_id": "WP001-SCHEMA",
        "attempt_id": attempt_id,
        "requirement_revision": "v0.1",
        "idempotency_key": "a" * 64,
        "actor": actor,
        "subject_builder": identity("CODEX:BUILDER", "BUILDER", "cred-codex", "session-codex") if role in policy["independence_required_roles"] or transition in policy["independence_required_transitions"] else None,
        "current_state": current,
        "target_state": target,
        "resulting_state": target,
        "evidence_inputs": [{"ref": evidence_ref, "sha256": sha256_bytes(evidence_bytes)}],
        "checks": checks,
        "declared_effective_verdict": "PASS",
        "created_at": "2026-09-15T00:00:00Z",
    }
    assigner = actor if role == "HUMAN" else identity("RAY:LEAD", "LEAD", "cred-ray", "session-ray")
    assignment = {
        "schema_version": "rayflow.role-assignment/v0.1",
        "task_id": record["task_id"],
        "attempt_id": attempt_id,
        "requirement_revision": record["requirement_revision"],
        "idempotency_key": record["idempotency_key"],
        "assignee": actor,
        "assigned_role": role,
        "assigned_by": assigner,
        "scope": transition,
        "authority_evidence": {
            "ref": authority_ref,
            "sha256": sha256_bytes(authority_path.read_bytes()),
            "method": "RAY_DECISION_RECORD",
        },
        "issued_at": "2026-09-15T00:00:00Z",
    }
    assignment_ref = f"assignments/{slug}.json"
    assignment_path = repo_root / assignment_ref
    assignment_path.parent.mkdir(parents=True, exist_ok=True)
    assignment_bytes = json.dumps(assignment, sort_keys=True, separators=(",", ":")).encode("utf-8")
    assignment_path.write_bytes(assignment_bytes)
    record["role_assignment_ref"] = assignment_ref
    record["role_assignment_sha256"] = sha256_bytes(assignment_bytes)
    return record, assignment, assignment_bytes, assignment_path


def self_test(policy: dict[str, Any]) -> list[tuple[str, bool, str]]:
    results: list[tuple[str, bool, str]] = []
    policy_errors = validate_policy(policy)
    results.append(("POLICY_STRUCTURE", not policy_errors, ",".join(policy_errors)))
    with tempfile.TemporaryDirectory(prefix="rayflow-role-gates-") as tmp:
        repo_root = Path(tmp)
        transition_errors: list[str] = []
        for transition in adjacent_transitions():
            candidate, assignment, assignment_bytes, assignment_path = valid_transition_run(policy, transition, repo_root)
            errors, computed, missing = validate_gate_run(candidate, policy, assignment, assignment_bytes, assignment_path, repo_root)
            if errors or computed != "PASS" or missing:
                transition_errors.append(f"{transition}:{','.join(errors)}:{','.join(sorted(missing))}")
        results.append(("ALL_TRANSITIONS_EXECUTABLE", not transition_errors, " | ".join(transition_errors)))

        valid, assignment, assignment_bytes, assignment_path = valid_transition_run(policy, "PUBLISHED->OBSERVED", repo_root)
        errors, computed, missing = validate_gate_run(valid, policy, assignment, assignment_bytes, assignment_path, repo_root)
        results.append(("ROLE_GATE_POSITIVE", not errors and computed == "PASS" and not missing, ",".join(errors)))

        self_verify = copy.deepcopy(valid)
        self_verify["actor"]["credential_ref"] = self_verify["subject_builder"]["credential_ref"]
        errors, computed, _ = validate_gate_run(self_verify, policy, assignment, assignment_bytes, assignment_path, repo_root)
        results.append(("NO_SELF_VERIFICATION", computed == "BLOCK" and "E_INDEPENDENCE_CREDENTIAL_REF_MATCH" in errors, ",".join(errors)))

        missing_gate = copy.deepcopy(valid)
        missing_gate["checks"] = missing_gate["checks"][1:]
        errors, computed, missing = validate_gate_run(missing_gate, policy, assignment, assignment_bytes, assignment_path, repo_root)
        results.append(("MISSING_GATE_BLOCKS", computed == "BLOCK" and bool(missing), ",".join(sorted(missing))))

        critical = copy.deepcopy(valid)
        critical["checks"][0]["critical"] = True
        critical["checks"][0]["observed"] = "MISSING"
        critical["checks"][0]["comparison"] = "MISSING"
        critical["checks"][0]["verdict"] = "UNKNOWN"
        errors, computed, _ = validate_gate_run(critical, policy, assignment, assignment_bytes, assignment_path, repo_root)
        results.append(("SINGLE_CRITICAL_UNKNOWN_BLOCKS", computed == "BLOCK", ",".join(errors)))

        proper_block = copy.deepcopy(critical)
        proper_block["declared_effective_verdict"] = "BLOCK"
        proper_block["resulting_state"] = "PUBLISHED"
        errors, computed, _ = validate_gate_run(proper_block, policy, assignment, assignment_bytes, assignment_path, repo_root)
        results.append(("BLOCK_CANNOT_ADVANCE_STATE", not errors and computed == "BLOCK", ",".join(errors)))

        wrong_role = copy.deepcopy(valid)
        wrong_role["actor"]["role"] = "BUILDER"
        errors, computed, _ = validate_gate_run(wrong_role, policy, assignment, assignment_bytes, assignment_path, repo_root)
        results.append(("TRANSITION_ROLE_ENFORCED", computed == "BLOCK" and any(e.startswith("E_ROLE_NOT_OWNER") for e in errors), ",".join(errors)))

        forged_assignment = copy.deepcopy(valid)
        forged_assignment["role_assignment_sha256"] = "f" * 64
        errors, computed, _ = validate_gate_run(forged_assignment, policy, assignment, assignment_bytes, assignment_path, repo_root)
        results.append(("ROLE_ASSIGNMENT_SHA_ENFORCED", computed == "BLOCK" and "E_ASSIGNMENT_SHA_MISMATCH" in errors, ",".join(errors)))

        tampered_evidence = copy.deepcopy(valid)
        tampered_evidence["evidence_inputs"][0]["sha256"] = "e" * 64
        errors, computed, _ = validate_gate_run(tampered_evidence, policy, assignment, assignment_bytes, assignment_path, repo_root)
        results.append(("EVIDENCE_SHA_READBACK_ENFORCED", computed == "BLOCK" and any(e.startswith("E_EVIDENCE_SHA_MISMATCH") for e in errors), ",".join(errors)))

        declared_pass = copy.deepcopy(valid)
        declared_pass["checks"][0]["observed"] = "FAIL"
        errors, computed, _ = validate_gate_run(declared_pass, policy, assignment, assignment_bytes, assignment_path, repo_root)
        results.append(("DECLARED_PASS_IS_RECOMPUTED", computed == "BLOCK" and any(e.startswith("E_CHECK_VERDICT_MISMATCH") for e in errors), ",".join(errors)))
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    default_policy = Path(__file__).resolve().parent.parent / "SCHEMA" / "rayflow-role-gates-v0.1.json"
    parser.add_argument("--policy", type=Path, default=default_policy)
    parser.add_argument("--gate-run", type=Path)
    parser.add_argument("--assignment", type=Path)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    policy = load_json(args.policy)
    failed = False
    policy_errors = validate_policy(policy)
    print("POLICY: " + ("PASS" if not policy_errors else "BLOCK | " + ",".join(policy_errors)))
    failed |= bool(policy_errors)

    if args.self_test:
        for name, passed, detail in self_test(policy):
            print(f"{name}: {'PASS' if passed else 'FAIL'}" + (f" | {detail}" if detail else ""))
            failed |= not passed

    if args.gate_run:
        if args.assignment is None or args.repo_root is None:
            missing_args = []
            if args.assignment is None:
                missing_args.append("E_ASSIGNMENT_REQUIRED")
            if args.repo_root is None:
                missing_args.append("E_REPO_ROOT_REQUIRED")
            print("EFFECTIVE_GATE=BLOCK")
            print("GATE_RUN: BLOCK | " + ",".join(missing_args))
            return 1
        record = load_json(args.gate_run)
        assignment_bytes = args.assignment.read_bytes()
        assignment = json.loads(assignment_bytes.decode("utf-8-sig"))
        errors, computed, missing = validate_gate_run(
            record,
            policy,
            assignment,
            assignment_bytes,
            args.assignment,
            args.repo_root,
        )
        print(f"EFFECTIVE_GATE={computed}")
        if missing:
            print("MISSING_GATES=" + ",".join(sorted(missing)))
        print("GATE_RUN: " + ("PASS" if not errors and computed == "PASS" else "BLOCK | " + ",".join(errors)))
        failed |= bool(errors) or computed != "PASS"

    if not (args.self_test or args.gate_run):
        parser.error("select --self-test and/or --gate-run")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
