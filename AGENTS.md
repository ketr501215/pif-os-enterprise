# PIF OS Enterprise — Agent execution rules

This file applies to every human or automated agent working anywhere in this
repository: Ray, Lead Agent, subagents, Claude Code, Codex, Gemini CLI,
Antigravity CLI, and later agents.

## Mandatory load order

Before accepting or changing a task, read:

1. `02_CONSTITUTION/PIF_OS_Constitution_v1.2.md`
2. `00_POCC/AGENT_RULES.md`
3. `08_AGENT_OS/RAYFLOW_ROLE_GATE_RULES_v0.1.md`
4. the applicable work package, task-state record, dependency graph, and latest
   valid supersession/correction records

Chat, memory, filenames, file existence, an agent-authored `PASS`, and cached
remote refs are pointers only. They are not authority or delivery evidence.

## Role declaration and mechanical gate

Every task attempt must declare exactly one acting role from `HUMAN`, `LEAD`,
`PLANNER`, `BUILDER`, `VERIFIER`, `ADVERSARY`, or `ORCHESTRATOR`. Product/vendor
names do not prove roles or independence. A subagent inherits only the
explicitly delegated scope; it does not inherit acceptance, verification, or
publication authority.

Before every state transition, the acting agent must create a
`rayflow.gate-run/v0.1` record and run:

```powershell
.\09_PROJECT_OS\TOOLS\Invoke-RoleGate.ps1 `
  -GateRun <gate-run.json> -Assignment <role-assignment.json>
```

Only `EFFECTIVE_GATE=PASS` permits the target state. `BLOCK`, `DEGRADED`, or
`UNKNOWN` leaves the task at its last proven durable state. Missing gate-run
evidence is `UNKNOWN`; for Critical work, `UNKNOWN => BLOCK`.

The assignment file and every gate evidence file must be inside the repository,
must be physically read, and must match the SHA recorded by the gate run. A
self-declared role string is never sufficient.

## Non-negotiable invariants

- `CREATED -> DISPATCHED -> ACCEPTED -> RUNNING -> PRODUCED -> PERSISTED ->
  PUBLISHED -> OBSERVED -> ACKED -> VERIFIED -> CLOSED` is monotonic and
  evidence-bound.
- A write is not a delivery. `PRODUCED != PUBLISHED`, `PUBLISHED != ACKED`, and
  `ACKED != VERIFIED`.
- Builder cannot observe, ACK, verify, adversarially clear, or close its own
  output.
- Verifier and Adversary must use source bytes and an independent method, not
  the Builder's conclusion or expected value.
- Gate results are computed from `expected -> live observation -> comparison`.
  A declared verdict is only a comparison target.
- A single Critical `BLOCK`, `UNKNOWN`, or `DEGRADED` forces effective `BLOCK`.
  Alarms are not votes.
- Write-period states require one current lease with actor-bound fencing and
  heartbeat. HOME and SCHOOL may not hold overlapping active leases.
- Restart or context compaction must reload canonical records, recompute the
  idempotency key, verify prior hashes, and reacquire/prove the lease. A summary
  cannot advance state.
- `CLOSED` requires a live Completion Proof, released-lease proof when a lease
  was used, all dependencies satisfied, independent verification, and Ray's
  explicit acceptance when required.
- Preserve unrelated changes. Never modify or publish secrets, customer data,
  credentials, raw sessions, or machine-local keys.

The normative role-to-gate mapping is
`09_PROJECT_OS/SCHEMA/rayflow-role-gates-v0.1.json`; prose summaries cannot
override it.
