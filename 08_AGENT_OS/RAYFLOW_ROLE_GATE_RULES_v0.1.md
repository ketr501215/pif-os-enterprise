# RayFlow Multi-Agent Orchestration Protocol — Role Gate Rules v0.1

Status: `ACTIVE BY RAY DECISION D010`

Authority quote: `請您把 RayFlow Multi-Agent Orchestration Protocol 中每位agent 角色該執行機械閘功能，納入工作規則中，要求所有agent 遵守`

## 1. Scope

These rules bind Ray, Lead Agent, every subagent, Claude Code, Codex, Gemini
CLI, Antigravity CLI, and future agents. They add mechanical execution duties;
they do not by themselves resolve the existing Constitution Article 6 versus
AGENT_RULES Article 13 communication conflict, activate all of WP001, or close
WP001.

Vendor diversity is not treated as independence. Each task attempt assigns a
role, identity, credential reference, session, machine/site, capability, and
method. The same product may take different roles on different tasks, but it
may not hold conflicting roles on the same task attempt.

Normative files:

- role policy: `09_PROJECT_OS/SCHEMA/rayflow-role-gates-v0.1.json`
- gate-run schema: `09_PROJECT_OS/SCHEMA/rayflow-gate-run-v0.1.schema.json`
- role-assignment schema:
  `09_PROJECT_OS/SCHEMA/rayflow-role-assignment-v0.1.schema.json`
- verifier: `09_PROJECT_OS/TOOLS/verify_role_gates.py`
- runtime resolver: `09_PROJECT_OS/TOOLS/Invoke-RoleGate.ps1`

## 2. Universal gate-run contract

Before an agent advances any lifecycle state, it must persist a gate-run record
containing:

- exact task, attempt, requirement revision, and idempotency key;
- actor role plus agent/vendor/credential/session/machine/site identity;
- current, target, and resulting state;
- hashed evidence inputs;
- every role and transition gate as `expected`, `observed`, `comparison`, and
  `verdict`;
- Critical classification and evidence reference;
- declared and mechanically computed effective verdict.

The verifier recomputes the verdict. The Agent's declared `PASS` has no
authority. Only a computed `PASS` may set `resulting_state=target_state`.
Otherwise `resulting_state` must remain the last proven `current_state`.

Each check uses one comparison code: `MATCH`, `MISMATCH`, `MISSING`, `STALE`,
`NOT_RUN`, or `DEGRADED`. The verifier derives PASS/BLOCK/UNKNOWN/DEGRADED from
that code and from exact expected/observed equality, then rejects any different
Agent-declared verdict.

The verifier also reads a separate `rayflow.role-assignment/v0.1` artifact,
checks its physical SHA, binds it to the exact task/attempt/idempotency key and
actor, and hashes its authority evidence. Every check's `evidence_ref` must be a
real repository file included in `evidence_inputs` with matching bytes. An
Agent cannot acquire a role by typing a different role name into its own gate
record.

## 3. Roles and required mechanical gates

### HUMAN — Ray / authorized human

Run:

- `HUMAN_AUTHORITY`: bind the exact human decision and its scope;
- `RISK_ACCEPTANCE_EXPLICIT`: record any explicit Critical-risk acceptance;
- `FINAL_ACCEPTANCE`: compare Completion Proof with acceptance criteria.

Human authority may accept risk but cannot manufacture missing SHA, delivery,
lease, ACK, or verification observations. Only HUMAN may authorize the final
`VERIFIED -> CLOSED` transition when the work package requires Ray acceptance.

### LEAD — Lead Agent

Run:

- `TASK_IDENTITY`: stable task ID, revision, destination and idempotency tuple;
- `DEPENDENCY_GRAPH`: exact nodes/edges, cycle detection and required states;
- `ROLE_SEPARATION`: no Builder self-ACK/self-verification;
- `CAPABILITY_ROUTE`: assigned actor has live operation-scoped capability;
- `GATE_AGGREGATION`: recompute alarms without voting.

The Lead may dispatch and aggregate. It may not replace missing specialist
evidence with a summary or mark its own build `VERIFIED/CLOSED`.

### ORCHESTRATOR — Lead Orchestrator / scheduler

Run all Lead gates plus:

- `STATE_TRANSITION`: target is the next adjacent state and prior evidence is
  complete;
- `IDEMPOTENCY_DEDUP`: deduplicate by `(idempotency_key, target_state)`;
- `LEASE_ROUTE`: select the one lawful HOME/SCHOOL/cloud writer;
- `RECOVERY_RELOAD`: after restart, reload canonical state and hashes.

The Orchestrator schedules work; it does not vote on substantive correctness.

### PLANNER

Run:

- `REQUIREMENT_FREEZE`: exact requirement revision and change boundary;
- `ACCEPTANCE_CRITERIA`: machine-verifiable success/failure criteria;
- `DEPENDENCY_GRAPH`: explicit acyclic dependencies;
- `EXPECTED_STATE_PRECOMMIT`: expected results fixed outside Builder output;
- `CRITICALITY_CLASSIFICATION`: Critical alarms and risk owner identified.

A Planner may propose tasks but cannot claim artifacts were produced,
published, ACKed, verified, or closed.

### BUILDER — implementation or artifact producer

Run:

- `BUILDER_CAPABILITY`: live write/push capability for exact actor and scope;
- `DEPENDENCIES_READY`: all required predecessor states observed;
- `WRITE_LEASE`: one current actor-bound lease and fencing token;
- `ARTIFACT_HASH`: path plus SHA-256 of produced source bytes;
- `PERSIST_READBACK`: durable store reads the same SHA;
- `PUBLISH_READBACK`: live destination/ref contains the exact commit and bytes;
- `NO_SELF_ACK`: Builder identity is excluded from observation/ACK/verification.

The Builder may report at most the highest state proven by these observations.
Writing a file is `PRODUCED`, not `PUBLISHED`.

### VERIFIER — recipient observer / independent verifier

Run:

- `OBSERVER_PROVENANCE`: verifiable session/credential/authority receipt;
- `OBSERVE_EXACT_ARTIFACT`: independently read path, commit and content SHA;
- `ACK_COMPARISON`: expected and observed repository/ref/path/commit/SHA match;
- `VERIFIER_PROVENANCE`: verifier identity differs from Builder identity;
- `METHOD_INDEPENDENCE`: runtime/schema/adversarial/property/hash method is
  independent of Builder's explanation;
- `ACCEPTANCE_CRITERIA_CHECK`: independently execute acceptance criteria;
- `CRITICAL_ALARM_SCAN`: emit all Critical PASS/BLOCK/DEGRADED/UNKNOWN results.

`observer != builder` must be mechanically recomputed from agent, credential,
and session evidence. A self-declared boolean is ignored.

### ADVERSARY — false-PASS and failure-path challenger

Run:

- `FALSE_PASS_INJECTION`: test missing/stale/self-authored evidence paths;
- `DOUBLE_EXECUTION_TEST`: test HOME/SCHOOL overlap and fencing;
- `SINGLE_CRITICAL_TEST`: prove one Critical alarm cannot be outvoted;
- `RESTART_COMPACTION_TEST`: tamper/missing-context/idempotency recovery tests;
- `WRITE_DELIVERY_SPLIT_TEST`: prove existence/write cannot imply delivery;
- `ADVERSARIAL_EVIDENCE`: persist exact cases, outputs and hashes.

The Adversary can raise a Critical alarm. It cannot clear one by silence or
majority vote and cannot close the task.

## 4. Product and subagent mapping

- Lead Agent defaults to `LEAD` or `ORCHESTRATOR`.
- A subagent must receive exactly one declared role and bounded scope. It has no
  authority outside that delegation.
- Codex defaults to `BUILDER` or `ORCHESTRATOR`, but may verify another Builder
  only with distinct provenance and method.
- Claude Code defaults to `VERIFIER` or `ADVERSARY`, but its name/model string
  is not identity evidence.
- Gemini CLI defaults to `PLANNER`, `VERIFIER`, or `ADVERSARY`; it must still
  satisfy provenance and method separation.
- Antigravity CLI is restricted to public-data `PLANNER`/`BUILDER` work unless
  a narrower policy explicitly grants more. It may not access private client
  data.

Defaults are routing hints, not permission. The task record controls.

## 5. Transition owners

| Transition | Required acting role |
|---|---|
| `CREATED -> DISPATCHED` | LEAD or ORCHESTRATOR |
| `DISPATCHED -> ACCEPTED` | assigned PLANNER, BUILDER, VERIFIER, ADVERSARY, LEAD or ORCHESTRATOR |
| `ACCEPTED -> RUNNING` | BUILDER or ORCHESTRATOR with write lease |
| `RUNNING -> PRODUCED` | BUILDER |
| `PRODUCED -> PERSISTED` | BUILDER |
| `PERSISTED -> PUBLISHED` | BUILDER or ORCHESTRATOR with live publication readback |
| `PUBLISHED -> OBSERVED` | VERIFIER |
| `OBSERVED -> ACKED` | VERIFIER |
| `ACKED -> VERIFIED` | VERIFIER; ADVERSARY findings included |
| `VERIFIED -> CLOSED` | HUMAN |

## 6. Fail-closed computation

```text
missing required gate or evidence                  => BLOCK
any Critical verdict != PASS                       => BLOCK
any required capability/lease/dependency != PASS   => BLOCK
any noncritical BLOCK or UNKNOWN                    => BLOCK
any noncritical DEGRADED                            => DEGRADED
otherwise                                           => PASS
```

`Alarm != Vote`. Three agents saying PASS cannot override one independently
evidenced Critical alarm.

## 7. Restart and compaction

Every resumed attempt keeps the logical idempotency key, creates a new attempt
ID only when authorized, verifies the previous snapshot/content/context SHA,
and reacquires or proves the live lease. If a prior single-use attempt was
consumed, a new authority is required; a repaired environment does not revive
the old authority.

## 8. Required check

All agents must run at repository root before relying on this policy:

```powershell
.\09_PROJECT_OS\TOOLS\Invoke-RoleGate.ps1 -SelfTest
```

A failed or unavailable verifier is `UNKNOWN => BLOCK`, not permission to skip
the gate.
