# Master Blueprint Index v0.1

Status: CANDIDATE / WP001 BLOCKED
Owner: Codex
Built from GitHub main base: `d655ea5228cdc386298863682e4ac55139f7a4c6`
Date: 2026-09-15

## Purpose

This index identifies the governing sources for PIF OS Enterprise and the first
minimal RayFlow implementation. It is an index, not an authority upgrade. A file
being listed or present does not mean that it is delivered, accepted, verified,
or closed.

## Authority and source map

| Priority | Source | Role | Current observation |
|---:|---|---|---|
| 1 | `02_CONSTITUTION/PIF_OS_Constitution_v1.2.md` | Highest declared governance | Active but conflicts with Article 13 on mailbox use; Claude Gate is BLOCK |
| 2 | `09_PROJECT_OS/DECISION_LOG.md` | Ray-approved project decisions | Must contain any decision that changes the Constitution or closes WP001 |
| 3 | `00_POCC/AGENT_RULES.md` | Operational agent rules | Article 13 uses STATUS/DAILY and forbids inbox/outbox |
| 4 | `09_PROJECT_OS/WORK_PACKAGE/WP001.md` | Work-package intent and acceptance route | `WAITING_REVIEW` at the starting snapshot; not CLOSED |
| 5 | `09_PROJECT_OS/REVIEW/WP001_REVIEW.md` | Independent Gate evidence | Claude verdict BLOCK at review commit `d655ea5...` |
| 6 | `PIF_OS_Enterprise_ADR001_完整討論紀錄_20260625.md` | Historical architecture record | Useful context; stale paths and numbering are not current authority |
| 7 | `00_POCC/SYNC_STATUS.md` | Claimed synchronization status | Not trusted without live HEAD/content comparison |
| 8 | `08_AGENT_OS/*/STATUS.md` | Agent operational pointers | Discovery only; cannot prove delivery or acceptance |

When two sources conflict, the higher authority governs and the gate fails
closed. No last-writer-wins or majority vote resolves a governance conflict.

## Current folder architecture

| Path | Function | Boundary |
|---|---|---|
| `00_POCC/` | Operating control center, risks, rules, sync claims | Claims require live evidence |
| `01_BUSINESS_OS/` | Offers and delivery board | No client-private data |
| `02_CONSTITUTION/` | Highest governance | Ray-controlled amendment |
| `03_MASTER_BLUEPRINT/` | Cross-system source map and build order | Index only |
| `04_KNOWLEDGE_OS/` | Shared KB and RayFlow schema design | No tenant/client payloads |
| `05_DOCUMENT_OS/` | Planned document generation layer | Not implemented in this snapshot |
| `06_RULE_ENGINE/` | Planned gate profiles and evaluators | Not implemented in this snapshot |
| `07_DATABASE/` | Planned persistence/schema layer | Not implemented in this snapshot |
| `08_AGENT_OS/` | Agent status and handoff rules | Status is not delivery proof |
| `09_PROJECT_OS/` | Work packages, reviews, state, ACK, verification, proof | Machine-readable lifecycle SSOT |
| `10_PRODUCT_LINES/` | Product-specific reference implementations | PIF/ISO 22716 is first |

## RayFlow v0.1 implementation map

| Artifact | Purpose |
|---|---|
| `04_KNOWLEDGE_OS/SCHEMA_v0.1.md` | Human-readable contract and transition rules |
| `09_PROJECT_OS/SCHEMA/task-state-v0.1.schema.json` | Machine-readable record shape |
| `09_PROJECT_OS/SCHEMA/WP001_dependency_graph.json` | Acyclic dependency graph separating WP001 and KB Schema gates |
| `09_PROJECT_OS/TOOLS/verify_task_state.py` | Fail-closed invariant checker and I1/T2/T4/T7/T8 tests |
| `09_PROJECT_OS/STATE/` | Durable task snapshots; later proof must bind exact commit and content SHA |
| `09_PROJECT_OS/ACK/` | Recipient-authored exact artifact observations and ACK decisions |
| `09_PROJECT_OS/VERIFICATION/` | Method-independent verification reports |
| `09_PROJECT_OS/COMPLETION_PROOF/` | Evidence index; never self-authorizes CLOSED |

## WP001 dependency order

1. Claude WP001 workflow Gate observes the published starting snapshot.
2. Critical governance conflict remains BLOCK until Ray authorizes the
   Constitution-first amendment.
3. Codex may produce and publish the Blueprint and Schema as candidate artifacts.
4. Claude independently observes the exact artifact commit and content SHA; this
   may ACK delivery without changing the parent Gate verdict.
5. A verifier using schema/runtime/adversarial checks evaluates T2/T4/T7/T8.
6. Completion Proof binds the immutable evidence and remains `closed=false`.
7. Only Ray acceptance, recorded after all blockers are cleared, may authorize
   the final `VERIFIED -> CLOSED` transition for WP001.

The machine-readable form is
`09_PROJECT_OS/SCHEMA/WP001_dependency_graph.json`.

## Sprint 2 minimal build order

1. Task-state contract and invariant verifier.
2. Exact artifact publication proof.
3. Recipient-side observation and ACK.
4. Independent method verification.
5. Incomplete Completion Proof awaiting Ray.
6. Constitution/protocol reconciliation only after explicit Ray decision.
7. Product-specific KB schemas and document gates after the lifecycle is trusted.

## HOLD boundaries

- `WP001 != CLOSED` while Claude Gate is BLOCK or Ray acceptance is absent.
- The current build does not amend Constitution v1.2 or activate a new protocol.
- A local file, commit message, status line, or agent assertion is not delivery.
- `GitHub READY` is forbidden as a global capability claim; READ and WRITE are
  observed per actor, credential reference, repository/ref, operation, and time.
- `PUBLISHED` requires live remote observation of the exact commit containing the
  exact content SHA.
- `ACKED` requires recipient-side expected/observed commit and content equality.
- `VERIFIED` requires a non-builder method and no Critical BLOCK/UNKNOWN.
- School/Home concurrency requires a single lease with fencing; hostname or site
  identity alone never grants write authority.
- No client data, credentials, raw sessions, or production PIF records belong in
  this repository.
