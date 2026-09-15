# Knowledge OS / RayFlow Task-State Schema v0.1

Status: CANDIDATE / NOT ACTIVATED
Task: `WP001-SCHEMA`
Builder: Codex
Base commit: `d655ea5228cdc386298863682e4ac55139f7a4c6`
Date: 2026-09-15

## 1. Scope

This is the smallest implementation contract needed to exercise WP001 without a
demo. It governs task state, dependency resolution, artifact delivery, ACK,
verification, Critical gates, cross-site leases, and restart recovery.

The normative machine-readable shape is
`09_PROJECT_OS/SCHEMA/task-state-v0.1.schema.json`. Cross-field invariants that
JSON Schema alone cannot express are checked by
`09_PROJECT_OS/TOOLS/verify_task_state.py`.

This file does not amend Constitution v1.2. Claude Gate remains BLOCK until the
higher-authority mailbox conflict is resolved and Ray accepts the change.

## 2. Minimal state machine

```text
CREATED -> DISPATCHED -> ACCEPTED -> RUNNING -> PRODUCED -> PERSISTED
        -> PUBLISHED -> OBSERVED -> ACKED -> VERIFIED -> CLOSED
```

Transitions are adjacent and monotonic. A later state requires all earlier
evidence; it is never inferred from file existence or an agent-authored status.

| Transition | Required evidence |
|---|---|
| `CREATED -> DISPATCHED` | Stable task ID, assignee, requirement revision, idempotency key |
| `DISPATCHED -> ACCEPTED` | Assignee acceptance bound to the same idempotency key |
| `ACCEPTED -> RUNNING` | Current unexpired lease and fencing token |
| `RUNNING -> PRODUCED` | Artifact path plus SHA-256 of produced bytes |
| `PRODUCED -> PERSISTED` | Durable local/store readback of the same SHA-256 |
| `PERSISTED -> PUBLISHED` | Live remote branch observation of a commit containing those exact bytes |
| `PUBLISHED -> OBSERVED` | Recipient independently reads exact path, commit, and content SHA |
| `OBSERVED -> ACKED` | ACK record says YES and expected equals observed for commit and content |
| `ACKED -> VERIFIED` | Independent method verdict PASS; no Critical BLOCK/UNKNOWN |
| `VERIFIED -> CLOSED` | All dependencies satisfied, lease released, Completion Proof complete, Ray acceptance where required |

`PRODUCED != PUBLISHED`, `PUBLISHED != ACKED`, and `ACKED != VERIFIED` are hard
invariants.

## 3. Machine-readable task record

Required top-level fields:

- `schema_version`, `task_id`, `work_package_id`, `title`
- `requirement_revision`, `idempotency_key`, `criticality`, `current_state`
- `actor`, `dependencies`, `artifact`, `delivery`, `verification`, `gate`
- `lease`, `recovery`, `history`, `updated_at`

The record is a durable snapshot. An implementation may additionally keep an
append-only event log, but no event log is required for v0.1.

### Artifact and commit proof

An artifact proof is valid only when all of these are true:

1. `artifact.path` is repository-relative and has no parent traversal.
2. `artifact.content_sha256` equals a fresh hash of the bytes.
3. `artifact.git_commit` is a full 40-hex commit.
4. Live `origin/<branch>` equals or contains that commit.
5. `git show <commit>:<path>` hashes to `artifact.content_sha256`.

The artifact commit cannot safely contain its own commit hash. Therefore the
publication/ACK/Completion Proof records are later artifacts that reference the
immutable artifact commit. This avoids a self-referential hash claim.

## 4. ACK definition

ACK is a recipient observation, not a sender assertion.

```text
ACK = YES only if
  expected_repository == observed_repository
  expected_branch == observed_branch
  expected_artifact_path == observed_artifact_path
  expected_commit == observed_commit
  expected_content_sha256 == observed_content_sha256
  observer != builder
  observation_method is recorded
```

Any mismatch gives `ACK = STALE` or `ACK = NO`; missing observation gives
`ACK = UNKNOWN`. None may advance to `ACKED`.

## 5. Completion Proof record

A Completion Proof is an evidence index with:

- task and requirement identity;
- idempotency key;
- artifact path, artifact commit, and content SHA;
- publication observation;
- recipient ACK reference and SHA;
- independent verification reference, method, and verdict;
- gate verdict and every alarm;
- lease release evidence;
- Ray acceptance reference when the work package requires it;
- `closed` boolean and explicit `not_closed_reasons`.

The record must remain `closed=false` when any required reference is absent. The
record itself cannot close its own task.

## 6. Machine-readable dependency solution

Every dependency edge identifies a specific task and required state. Free-text
phrases such as `waiting for Claude` are prohibited as authority.

For WP001, the graph separates:

- `WP001_WORKFLOW_GATE`: Claude reviews the existing workflow; it has no Schema
  dependency.
- `WP001_SCHEMA_BUILD`: Codex builds the schema; it may proceed as candidate work
  after the first Gate observation even while the parent remains BLOCK.
- `WP001_SCHEMA_ACK`: Claude observes the exact Schema artifact commit.
- `WP001_SCHEMA_VERIFY`: independent method checks T2/T4/T7/T8.
- `WP001_RAY_ACCEPTANCE`: depends on the governance conflict being cleared and
  all prior nodes being VERIFIED.

A cycle detector must run before dispatch. A graph cycle, missing node, or
ambiguous free-text dependency is `UNKNOWN => BLOCK`.

## 7. Idempotency key

Use one stable key per logical task/revision/destination:

```text
sha256(
  repository + "\n" +
  task_id + "\n" +
  requirement_revision + "\n" +
  artifact_path + "\n" +
  target_branch
)
```

Retries or restarts reuse the same idempotency key and create a new `attempt_id`.
The system deduplicates the logical transition by `(idempotency_key, target_state)`.
A different key is a different logical operation and cannot silently replace a
blocked attempt.

## 8. School/Home lease and heartbeat

The lease key is the governed resource, for example `repo:WP001`. Its minimal
record contains `lease_id`, `holder_agent_id`, `machine_id`, `site`,
`fencing_token`, `heartbeat_at`, `expires_at`, and `status`.

Rules:

1. Acquire by compare-and-swap on the current fencing token.
2. One resource may have at most one unexpired ACTIVE lease across HOME/SCHOOL.
3. Heartbeat extends only the same `lease_id` with the same fencing token.
4. Every write/transition carries the current fencing token.
5. After expiry, takeover increments the fencing token and records predecessor
   lease evidence; an old holder is fenced even if it resumes later.
6. Close requires RELEASED evidence. Missing/ambiguous lease state is UNKNOWN
   and blocks write transitions.

This prevents T4 double execution without relying on device names or clocks as
authority.

## 9. Fail-closed Gate

The effective Gate is computed, not copied from an agent report:

```text
if any Critical alarm is BLOCK:                 BLOCK
else if any Critical alarm is UNKNOWN:          BLOCK
else if required evidence is absent/stale:      BLOCK
else if independent verification is not PASS:   BLOCK
else if any noncritical alarm is DEGRADED:       DEGRADED
else:                                           PASS
```

Votes are not inputs. One Critical alarm cannot be outvoted. An agent-authored
`PASS` without the expected-state/live-observation comparison is ignored.

## 10. Restart and context-compaction recovery

On restart:

1. Load the latest durable task snapshot and verify its schema/invariants.
2. Verify the last artifact/ACK/proof hashes from their source bytes.
3. Reuse the same idempotency key; create a new attempt ID only if execution is
   resumed.
4. Reacquire or prove the lease; never trust a pre-restart heartbeat.
5. Resume from the last state with complete evidence. Do not infer the next state
   from a summary, filename, or existence check.
6. Treat context-compaction summaries as pointers only. Bind a summary digest in
   `recovery.context_digest`, but re-read the canonical records.
7. Broken history, missing proof, stale commit, or ambiguous lease is UNKNOWN and
   therefore BLOCK for Critical work.

## 11. WP001 first-loop expected evidence

The current run must produce evidence in this order:

1. Claude Gate review commit and live remote observation.
2. Codex artifact commit for this file and the Blueprint.
3. Live GitHub observation of that exact commit and artifact hash.
4. Claude-authored ACK comparing expected and observed values.
5. Independent runtime/schema/adversarial verification of T2/T4/T7/T8.
6. Completion Proof with `closed=false` and Ray acceptance absent.

Even if steps 2 through 5 pass, the parent WP001 remains BLOCKED by the current
Constitution conflict and remains not CLOSED until Ray acts.

## 12. Acceptance tests

Run:

```powershell
python .\09_PROJECT_OS\TOOLS\verify_task_state.py --self-test
python .\09_PROJECT_OS\TOOLS\verify_task_state.py --graph .\09_PROJECT_OS\SCHEMA\WP001_dependency_graph.json
```

Required test outcomes:

- T2: closing after PRODUCED/PUBLISHED without ACK/verification is rejected.
- T4: overlapping HOME/SCHOOL ACTIVE leases are rejected.
- T7: one Critical UNKNOWN/BLOCK makes the effective Gate BLOCK.
- T8: restart with matching durable evidence resumes idempotently; missing or
  changed evidence blocks.
