# PIF OS Enterprise — Agent Handoff Protocol v0.2

Status: `ACTIVE BY RAY DECISION D010`

Supersedes: `08_AGENT_OS/AGENT_HANDOFF_PROTOCOL_v0.1.md`

## 1. Authority and load order

All agents first read the repository `AGENTS.md`, Constitution,
`00_POCC/AGENT_RULES.md`, and
`08_AGENT_OS/RAYFLOW_ROLE_GATE_RULES_v0.1.md`. The v0.1 protocol remains
historical and must not be edited to simulate prior compliance.

The existing Constitution Article 6 versus AGENT_RULES Article 13
communication conflict remains an explicit Critical HOLD. This protocol does
not silently choose between mailbox and STATUS-only transport. Whichever
transport is lawfully selected must still carry the evidence below.

## 2. Dispatch

A dispatch is valid only when it identifies:

- task ID, requirement revision, target artifact/ref and idempotency key;
- assigned agent identity, one assigned role and operation capability;
- exact dependency nodes and required states;
- acceptance criteria and precommitted expected evidence;
- lease resource and site when writes are possible;
- Critical alarms and escalation owner.

The Lead/Orchestrator runs the `CREATED -> DISPATCHED` role gate. The recipient
runs its own `DISPATCHED -> ACCEPTED` gate. File presence alone is not
acceptance.

## 3. Work and delivery

Write-period transitions require a current actor-bound lease and fencing token.
The Builder records artifact SHA, persistence readback, and live publication
readback separately:

```text
RUNNING -> PRODUCED -> PERSISTED -> PUBLISHED
```

A handoff that stops at `PRODUCED` or `PERSISTED` must state that it was not
delivered. Git commit without live remote observation is not publication.

## 4. Observation, ACK and verification

The recipient Verifier independently reads exact repository/ref/path/commit and
content SHA. It records observer session/credential provenance and mechanically
compares expected versus observed values before ACK.

The independent verification stage must use a different method from the
Builder's production method. Reading or paraphrasing the Builder's report is not
verification. An Adversary tests false-PASS, double-execution, single-Critical,
write-versus-delivery and restart/compaction paths.

```text
PUBLISHED -> OBSERVED -> ACKED -> VERIFIED
```

No stage may be inferred from a later filename or an Agent-authored `PASS`.

## 5. Close

The Lead assembles but cannot self-approve the Completion Proof. Only the HUMAN
role may perform `VERIFIED -> CLOSED` where Ray acceptance is required. The
mechanical close gate requires dependency satisfaction, released-lease proof,
publication, ACK, independent verification, every alarm, and exact Ray
acceptance evidence.

## 6. Restart, compaction and duplicate delivery

On restart, re-read canonical state and evidence bytes, recompute the stable
idempotency key, bind the previous snapshot/context hashes, and reacquire or
prove the lease. A new attempt ID does not permit a second delivery for the same
`(idempotency_key, target_state)`. A consumed single-use authority cannot be
revived by repairing the environment.

## 7. Required mechanical record

Every transition handoff includes a `rayflow.gate-run/v0.1` record validated by:

```powershell
.\09_PROJECT_OS\TOOLS\Invoke-RoleGate.ps1 `
  -GateRun <gate-run.json> -Assignment <role-assignment.json>
```

Missing verifier output, unavailable runtime, missing provenance, or stale
evidence is `UNKNOWN`; Critical work therefore remains `BLOCK`.
