# WP001-SCHEMA — Bootstrap Ruling (pre-lease writes)

Status: BOOTSTRAP RULING (durable — governs lifecycle transitions of this artifact only)
Reviewer: Claude Code (Gate Reviewer, independent of builder)
Companion review: `09_PROJECT_OS/REVIEW/WP001_SCHEMA_PREPUBLICATION_CLAUDE.md`
Date issued: 2026-09-15
Base tree: uncommitted working tree at issuance

This file addresses a distinct question from the pre-publication review: even if
the artifact CONTENT independently verifies PASS, may the artifact's own task
record honestly reach `current_state=VERIFIED` when RayFlow lease machinery did
not exist during its RUNNING/PRODUCED/PERSISTED transitions?

---

## 1. Observed situation

- The `04_KNOWLEDGE_OS/SCHEMA_v0.1.md` artifact was built and published **before**
  the RayFlow lease machinery (`verify_task_state.py` lease invariants + peer
  lease exclusion) existed.
- There is therefore **no actual task-specific lease acquisition, heartbeat, or
  release record** for those historical write-period transitions. No
  `lease_id`, no fencing token, no `heartbeat_at` / `expires_at` window, and no
  release observation was ever produced for THIS artifact.
- The verifier's `T4_*` self-tests prove the invariant enforces correctly on
  synthetic inputs; the independent adversary's runtime replay of the official
  self-test + graph confirmed exit 0 on the current tree.
- Neither of the above constitutes lease evidence for the historical writes of
  this specific artifact.

## 2. Fail-closed ruling

**The durable task record for `WP001-SCHEMA` MUST NOT claim
`current_state=VERIFIED` (and MUST NOT claim `CLOSED`).**

The highest honest delivery milestone reachable from evidence-in-hand is
`current_state = ACKED`. Any attempt to advance beyond `ACKED` without either
(a) a Ray-signed bootstrap exception or (b) a lease-governed re-attempt is
fabrication and violates SCHEMA §8 + §10.7.

Concurrently, the lifecycle Gate for this record MUST compute BLOCK by carrying a
CRITICAL alarm:

```
alarm_id      : A_BOOTSTRAP_LEASE_PROVENANCE_UNKNOWN
severity      : CRITICAL
verdict       : UNKNOWN
evidence_ref  : 09_PROJECT_OS/REVIEW/WP001_SCHEMA_BOOTSTRAP_CLAUDE.md
```

Per SCHEMA §9 the effective Gate is BLOCK while this alarm is present and
unresolved. `gate.declared_verdict` MUST also be `BLOCK` (or verifier will emit
`E_GATE_COMPUTATION_MISMATCH`).

### 2.1 Why T4 test PASS is not lease evidence

- Passing `T4_SCHOOL_HOME_DOUBLE_EXECUTION`, `T4_EXPIRED_LEASE_BLOCKS`, and
  `T4_RUNNING_REQUIRES_ACTIVE_LEASE` shows that the RULE enforces correctly on
  synthetic records.
- It does not show that the RULE was APPLIED to this artifact's historical
  writes. Rule-existence ≠ rule-application. Substituting the former for the
  latter is the exact category error SCHEMA §9 rejects:
  *"An agent-authored PASS without the expected-state/live-observation
  comparison is ignored."*
- Independent adversary runtime PASS on the verifier itself is likewise a
  test-of-machinery, not a test-of-history.

### 2.2 Why a test-report / synthetic file must not be `lease_release_evidence`

- The field's semantic meaning is: "record of THIS task acquiring, heart-beating,
  and releasing THE lease for its own write period." A lease that was never
  acquired cannot be released; a released-lease reference cannot exist.
- The current verifier only checks that `lease_release_evidence` is a non-empty
  string (`verify_task_state.py:298–299` in the reviewed tree — see §5 note).
  That is a fail-open edge; the fail-closed reading of the SCHEMA still forbids
  synthetic evidence there.
- The correct value under `lease.status=NONE` is `null` (schema allows nullable),
  paired with the CRITICAL alarm above.

## 3. Highest honest lifecycle state and required record shape

| Field | Required value |
|---|---|
| `current_state` | `ACKED` (not VERIFIED, not CLOSED) |
| `history[]` last event `to` | `ACKED`; no fabricated RUNNING/PRODUCED/PERSISTED events with fake lease `evidence_ref` |
| `lease.status` | `NONE` |
| `lease.lease_id` / `heartbeat_at` / `expires_at` | `null` |
| `lease.resource` | canonical (e.g. `repo:wp001`) |
| `completion_proof.lease_release_evidence` | `null` |
| `completion_proof.evaluation_mode` | `LIVE` |
| `gate.alarms[]` | includes `A_BOOTSTRAP_LEASE_PROVENANCE_UNKNOWN` (CRITICAL / UNKNOWN) |
| `gate.declared_verdict` | `BLOCK` |
| `gate.computed_verdict` | `BLOCK` (per §9) |
| `parent_wp001_gate` | `BLOCK` (Constitution v1.2 mailbox conflict) |
| `wp001_closed` | `false` |
| `ray_acceptance_present` | `false` |

The record must not silently backfill any lease event. History that never
happened does not become history because it would have been convenient.

## 4. Two — and only two — paths forward (both fail-closed)

Both paths preserve the invariant that write-period transitions require
lease-governed evidence, without falsifying observational history.

### Path A — Ray-signed bootstrap exception (minimal cost, still honest)

1. Ray writes an explicit decision in `09_PROJECT_OS/DECISION_LOG.md`
   (or equivalent governance file) stating:
   - Which artifact + which commit + which content SHA is granted the exception.
   - The reason: RayFlow lease machinery post-dated the artifact's writes.
   - The compensating control: all future writes on `repo:wp001` MUST be
     lease-governed, and the artifact's *content* is independently replayed.
2. The `A_BOOTSTRAP_LEASE_PROVENANCE_UNKNOWN` alarm remains **present** in the
   record for audit; its `verdict` may be flipped from `UNKNOWN` → `PASS` with
   its `evidence_ref` updated to point to the Ray decision commit/anchor.
   The alarm entry must NOT be deleted (deletion = falsification).
3. `completion_proof.ray_acceptance` is set to the Ray decision reference.
4. Only after (1)–(3) may `current_state` advance to `VERIFIED`.
5. `CLOSED` still requires `parent_wp001_gate` to clear, which the mailbox
   conflict currently blocks — independent of this ruling.

### Path B — Lease-governed re-attempt (technically clean, higher cost)

1. Open a new `attempt_id` (attempt-2 or later) under the same
   `idempotency_key` (which is invariant per SCHEMA §7).
2. Under the new attempt, actually acquire the lease for `repo:wp001`, run the
   heartbeat, and release it — producing real `lease_id`, fencing token, and
   release observation records.
3. Since the content SHA and commit are already correct, the write-period
   states can be re-entered as no-ops that only produce the missing lease
   evidence; content bytes are unchanged.
4. `history[]` for the new attempt reflects real events; the bootstrap alarm
   from attempt-1 is preserved in the recovery/history chain for audit but the
   new attempt reaches `VERIFIED` on its own evidence.

Path B is stronger but expensive for a documentation artifact; Path A is
recommended as the minimum non-fabricated remedy.

## 5. Cross-agent agreement

- **Codex (builder)** and the **independent adversary** both agree not to
  advance the record to `VERIFIED` on the strength of T4 synthetic/runtime
  PASS alone. Neither will fabricate `lease_release_evidence` from test
  artifacts. This ruling is issued in concurrence, not in opposition.
- **Codex has since added** `T4_BOOTSTRAP_WITHOUT_LEASE_BLOCKS` and stricter
  `RELEASED` evidence validation to `verify_task_state.py`. This closes the
  fail-open edge noted in §2.2 (unchecked truthy `lease_release_evidence`) and
  automates the enforcement of §2 at the verifier level.
- **Claude has NOT runtime-replayed** the latest patch containing
  `T4_BOOTSTRAP_WITHOUT_LEASE_BLOCKS` / stricter RELEASED evidence. Claude's
  confirmation of that patch remains **static review only**; runtime verdict on
  that specific patch must come from the independent adversary or a second-party
  replay before it is treated as observed.

## 6. Companion verdict (unchanged)

- `CLAUDE_BOOTSTRAP_RULING = BLOCK` (lifecycle Gate for WP001-SCHEMA record)
- `CLAUDE_REVIEW (candidate artifact content)` = `PREPUBLICATION_PASS`
  (per companion file — content-level; does not lift the lifecycle Gate)
- `PARENT_WP001_GATE = BLOCK`
- `WP001_CLOSED = false`
- `HIGHEST_HONEST_STATE_FOR_THIS_RECORD = ACKED`
- `PATH_TO_VERIFIED` requires Path A (Ray exception) or Path B (re-attempt);
  no third path is admissible.

This ruling is durable: it does not expire on time and does not evaporate on
context compaction. It is superseded only by an explicit Ray decision (Path A)
or by a lease-governed re-attempt satisfying the verifier under the current
patched machinery (Path B).
