# PIF OS Enterprise Folder Naming Standard v0.1

Date: 2026-06-25
Status: Active for next-boot handoff
Owner: Ray
Agents: ChatGPT = Chief Architect/PMO; Codex = Builder/implementation; Claude Code = reviewer/QC; Gemini = constitution/knowledge synthesis

## Binding Decision

The coordination folder name is fixed as:

- `00_POCC`

Do not use agent names in formal folder names. Historical aliases such as `00_POCC (Claude code)` are retired and must not be recreated.

## Current Live Root

Current live workspace:

- `F:\42-0 一人公司-規劃與運作\PIF_OS`

The ADR/Constitution proposed canonical enterprise repository name is:

- `PIF_OS_ENTERPRISE`

For 2026-06-25 execution, do not move the live root. Treat `PIF_OS` as the current governed root and record `PIF_OS_ENTERPRISE` as the intended GitHub/private repository name.

## Root Structure

| Folder | Purpose | First owner |
|---|---|---|
| `00_POCC` | Project operating control center, agent handoff, status, gate, sync | ChatGPT + Claude + Codex |
| `01_BUSINESS_OS` | Offer catalog, delivery board, renewal/commercial operations | Codex drafts, Ray approves |
| `02_CONSTITUTION` | Constitution and governance rules | Gemini/ChatGPT drafts, Ray approves |
| `03_MASTER_BLUEPRINT` | Master architecture and roadmap | ChatGPT owns |
| `04_KNOWLEDGE_OS` | Regulatory and ingredient knowledge base | Gemini + Codex |
| `05_DOCUMENT_OS` | PIF/ISO/GMP document generation system | Codex + Claude |
| `06_RULE_ENGINE` | Compliance rules, gates, calculators | Codex owns, Claude reviews |
| `07_DATABASE` | Schemas, fixtures, local DB strategy | Codex owns |
| `08_AGENT_OS` | Agent roles, handoff grammar, review protocol | ChatGPT + Claude |
| `09_PROJECT_OS` | Work packages, sprint boards, client delivery tracking | POCC |
| `10_PRODUCT_LINES/PIF_ISO22716` | First revenue/reference implementation | Codex + Claude |
| `11_RELEASE` | Release packages, SHA logs, signed outputs | POCC |
| `12_CLIENTS_Private` | Client-confidential data; never upload to public/cloud AI | Ray only unless authorized |
| `99_ARCHIVE` | Deprecated or superseded material | POCC |

## Rules

1. Formal folders use numeric prefixes and uppercase snake/camel descriptors.
2. Agent names may appear in file names for mailbox exchange, not in folder names.
3. No destructive rename or relocation without a written POCC decision record.
4. `12_CLIENTS_Private` is excluded from Git backup by default.
5. A folder is considered established only when it has a clear owner, purpose, and next action.
