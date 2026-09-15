# Knowledge OS / RayFlow Task-State Schema v0.1

Status: CANDIDATE / NOT ACTIVATED
Task: `WP001-SCHEMA`
Builder: Codex
Base commit: `d655ea5228cdc386298863682e4ac55139f7a4c6`
Date: 2026-09-15

## 1. Scope

This is the smallest implementation contract needed to exercise WP001 without a
demo. It governs task state, dependency resolution, artifact delivery, ACK,
verification, operation-scoped capabilities, Critical gates, cross-site leases,
and restart recovery.

The normative machine-readable shape is
`09_PROJECT_OS/SCHEMA/task-state-v0.1.schema.json`. Cross-field invariants that
JSON Schema alone cannot express are checked by
`09_PROJECT_OS/TOOLS/verify_task_state.py`.

Ray decision D010 separately activates the all-Agent role gate rule for new
task actions. Its normative mapping is
`09_PROJECT_OS/SCHEMA/rayflow-role-gates-v0.1.json`; every attempted state
transition must produce a `rayflow.gate-run/v0.1` record and pass
`09_PROJECT_OS/TOOLS/Invoke-RoleGate.ps1`. This activation does not activate the
remainder of this candidate schema or close WP001.

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
- `actor`, `capabilities`, `dependencies`, `artifact`, `delivery`, `verification`, `gate`
- `lease`, `recovery`, `completion_proof`, `history`, `updated_at`

The record is a durable snapshot. An implementation may additionally keep an
append-only event log, but no event log is required for v0.1.

### Operation-scoped capability evidence

There is no global `GitHub READY`. Each capability observation is scoped to:

```text
actor + credential_ref + machine/site + repository/ref + operation + observed_at
```

`READ`, `WRITE`, `CREATE_ISSUE`, `PUSH`, and `ACK` are separate and not
interchangeable. The delivery record names the exact required publish operation.
A successful read cannot imply a successful push. If the assigned actor and
current credential reference, machine, and site have any computed BLOCK/UNKNOWN
observation in the same repository/ref/operation scope, `PUBLISHED` is blocked
even when an older observation says PASS or another actor can push successfully.
The capability verdict is recomputed from `observed_outcome` and `result_code`;
the stored verdict is only a comparison target. Credential references are opaque
fingerprints; secrets must never enter the record.

Ray reported a GitHub path with `READ_READY / WRITE_FAIL_403`; this is retained
as user-reported evidence until the exact actor/operation/time response is
persisted and independently reproduced or validated. In the same session,
Codex pushes succeeded. These observations are actor-scoped, not contradictory
global service states.

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

Live proof also compares the task record repository identity with the checkout
`origin` URL. Bytes from a different repository cannot satisfy the proof.

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

The machine record uses separate `publication_ref`, `ack_ref`,
`verification_ref`, and `gate_ref` fields. A generic non-empty evidence list is
not sufficient. It also records `evaluation_mode` and `evaluated_at`;
`HISTORICAL` proof is forensic evidence and cannot satisfy a live Gate.

## 6. Machine-readable dependency solution

Every dependency edge identifies a specific task and required state. Free-text
phrases such as `waiting for Claude` are prohibited as authority.

For WP001, the graph separates:

- `WP001_WORKFLOW_GATE`: Claude reviews the existing workflow; it has no Schema
  dependency.
- `WP001-SCHEMA`: one lifecycle task whose milestones are Codex publication,
  Claude exact-artifact ACK, and independent T2/T4/T7/T8 verification. It may
  proceed as candidate work after the workflow Gate is observed even while the
  parent remains BLOCK.
- `WP001_RAY_ACCEPTANCE`: depends on the governance conflict being cleared and
  all prior nodes being VERIFIED.

A cycle detector must run before dispatch. A graph cycle, missing node, or
ambiguous free-text dependency is `UNKNOWN => BLOCK`. A VERIFIED/CLOSED task
record must also be checked against this graph: its task node must exist, every
declared edge must be present with the graph-required state and evidence, and
undeclared edges are rejected.

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

`RUNNING`, `PRODUCED`, and `PERSISTED` are write-period states and require an
unexpired ACTIVE lease whose holder, machine, and site match the task actor.
"Unexpired" is evaluated against the verifier's live UTC wall clock, not merely
against the record's self-declared `updated_at`; a mutually consistent historical
lease window is still expired for a live Gate.
The lease may be released after PUBLISHED because remote bytes are then durable;
VERIFIED requires `status=RELEASED` plus release evidence included in the
Completion Proof evidence set, so `status=NONE` or a generic T4 test report
cannot fabricate a historical release. A lifecycle history containing write
states while lease status is NONE is explicitly blocked.

`lease_release_evidence` is an artifact proof object, not a free-text path. It
binds repository, branch, receipt path, receipt commit, and receipt SHA-256. The
verifier reads those committed bytes from a live-observed branch and requires a
`rayflow.lease-release/v0.1` receipt whose task, resource, lease ID, holder,
machine/site, fencing token, heartbeat, expiry, and RELEASED status match the
task record. A missing file or plausible-looking filename remains BLOCK.

This prevents T4 double execution without relying on device names or clocks as
authority.

## 9. Fail-closed Gate

The effective Gate is computed, not copied from an agent report:

```text
if any Critical alarm is BLOCK:                 BLOCK
else if any Critical alarm is UNKNOWN:          BLOCK
else if required operation capability is not PASS: BLOCK
else if required evidence is absent/stale:      BLOCK
else if independent verification is not PASS:   BLOCK
else if any noncritical alarm is DEGRADED:       DEGRADED
else:                                           PASS
```

Votes are not inputs. One Critical alarm cannot be outvoted. An agent-authored
`PASS` without the expected-state/live-observation comparison is ignored.
The operation capability used for publication must be observed within 24 hours;
an older success becomes UNKNOWN and cannot mask a newer denial such as HTTP 403.

## 10. Restart and context-compaction recovery

On restart:

1. Load the latest durable task snapshot and execute both JSON Schema validation
   and cross-field invariant checks.
2. Verify the last artifact/ACK/proof hashes from their source bytes.
3. Recompute the idempotency key from the canonical task tuple. On resume, bind
   the exact previous snapshot bytes, previous idempotency key, artifact SHA, and
   context file SHA; create a new attempt ID only if execution is resumed.
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
python .\09_PROJECT_OS\TOOLS\verify_task_state.py .\09_PROJECT_OS\STATE\WP001-SCHEMA.json --graph .\09_PROJECT_OS\SCHEMA\WP001_dependency_graph.json --repo-root . --previous-state <path-when-resuming>
```

Required test outcomes:

- I1: `READ=PASS` plus assigned-writer `WRITE=FAIL_403` cannot become PUBLISHED.
- T2: closing after PRODUCED/PUBLISHED without ACK/verification is rejected.
- T4: overlapping HOME/SCHOOL ACTIVE leases are rejected.
- T4: a self-consistent but historically expired ACTIVE lease is rejected by
  the live wall clock.
- T7: one Critical UNKNOWN/BLOCK makes the effective Gate BLOCK.
- T8: restart with matching durable evidence resumes idempotently; missing or
  changed evidence blocks.

The record command performs a live `git ls-remote`, proves the artifact commit is
an ancestor of current remote main, extracts committed bytes with `git show`, and
compares their SHA-256. A syntactically plausible commit or hash is insufficient.
`--as-of <timestamp>` is forensic replay only: its output is explicitly marked
HISTORICAL and can never produce a live VERIFIED/CLOSED Gate result.
