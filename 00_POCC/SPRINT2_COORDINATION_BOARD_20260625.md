# Sprint 2 Coordination Board - 2026-06-25

Status: Active
Scope: One-person-company AI Operating System

## Sprint 2 North Star

Build the first reusable company architecture layer before expanding PIF-specific implementation.

## Direct Coordination Items

| ID | Item | Decision Needed | Owner | Due | Status |
|---|---|---|---|---|---|
| S2-001 | Master Blueprint Index | Confirm source-of-truth map across Constitution, ADR001, ChatGPT blueprint, POCC | Codex | Next boot first task | READY |
| S2-002 | Knowledge OS Schema | Use `04_KNOWLEDGE_OS`, not `20_KNOWLEDGE_OS` | Codex | Sprint 2 P0 | READY |
| S2-003 | Source Registry | Define evidence/source/provenance/version fields | Codex | Sprint 2 P0 | READY |
| S2-004 | Agent Handoff Protocol | Tighten daily mailbox grammar and review file naming | Claude | Sprint 2 P0 | READY |
| S2-005 | Business OS Enrichment | Fill offers and delivery stages without leaking private client data | Codex + Ray | Sprint 2 P1 | WAIT_RAY_FOR_FINAL_PRICES |
| S2-006 | PIF/ISO Bug Locator Pack | Move bug details to product-line folder | Claude | Sprint 2 P1 | WAIT_LOCATORS |
| S2-007 | GitHub Backup Discipline | Every Sprint 2 change must commit, push, and update sync status | Codex | Continuous | ACTIVE |

## Non-Goals For Sprint 2 P0

- Do not restart 80-row chase as company-level P0.
- Do not push client/private files to GitHub.
- Do not rename `00_POCC`.
- Do not move the live root unless Ray explicitly approves a migration plan.

## Next Boot First Command Set

```powershell
cd 'F:\42-0 一人公司-規劃與運作\PIF_OS'
git status --short
git log --oneline -5
Get-Content -Raw -Encoding UTF8 '.\00_POCC\SPRINT2_COORDINATION_BOARD_20260625.md'
Get-Content -Raw -Encoding UTF8 '.\00_POCC\CODEX_TO_CLAUDE_SPRINT2_REPLY_20260625.md'
```

## First Build Package

Create these five files first:

1. `03_MASTER_BLUEPRINT/MASTER_BLUEPRINT_INDEX_v0.1.md`
2. `04_KNOWLEDGE_OS/SCHEMA_v0.1.md`
3. `04_KNOWLEDGE_OS/SOURCE_REGISTRY_v0.1.md`
4. `04_KNOWLEDGE_OS/REGULATORY_KB_SCHEMA_v0.1.md`
5. `04_KNOWLEDGE_OS/INGREDIENT_KB_SCHEMA_v0.1.md`

## Architecture Discussion Reply Status

Date: 2026-06-25

| Item | File | Status | Next Owner |
|---|---|---|---|
| Codex multitenant architecture reply | `00_POCC/CODEX_TO_CLAUDE_ARCH_REPLY_20260625.md` | READY_FOR_GATE | Claude Code |
| Claude Gate review | `00_POCC/CLAUDE_TO_CODEX_ARCH_REVIEW_20260625.md` | WAITING | Claude Code |
| Ray final promotion | AGENT_RULES / schema build approval | WAITING | Ray |

## Daily Report Rule Status

Date: 2026-06-25

| Item | File | Status | Next Owner |
|---|---|---|---|
| S2-008 Daily report protocol | `08_AGENT_OS/DAILY_REPORT_PROTOCOL_v0.1.md` | ACTIVE | All Agents |
| Codex daily report | `08_AGENT_OS/Codex/DAILY_Codex_20260625.md` | CREATED | Codex |
| ChatGPT daily report placeholder | `08_AGENT_OS/ChatGPT/DAILY_ChatGPT_20260625.md` | WAITING_FOR_CHATGPT_CONTENT | ChatGPT |

## ChatGPT Daily Report Enhancement Proposal

Date: 2026-06-25

| Item | File | Status | Next Owner |
|---|---|---|---|
| Constitution Project Priority Governance proposal | `00_POCC/CHATGPT_TO_ALL_DAILY_REPORT_ENHANCEMENT_20260625.md` | RECEIVED_AS_PROPOSAL | Claude Code + Ray |
| Add Need Review / Need Ray Decision / Next Agent fields | `00_POCC/CHATGPT_TO_ALL_DAILY_REPORT_ENHANCEMENT_20260625.md` | PENDING_RULE_UPDATE | Claude Code + Ray |
| Constitution v1.1 to v1.2 upgrade | `02_CONSTITUTION/PIF_OS_Constitution_v1.2.md` | NOT_STARTED | Claude Code |
