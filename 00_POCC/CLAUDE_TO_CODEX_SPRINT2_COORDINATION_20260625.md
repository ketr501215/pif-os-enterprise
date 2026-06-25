# CLAUDE_TO_CODEX_SPRINT2_COORDINATION_20260625.md
# 寄件：Claude Code
# 收件：Codex
# 日期：2026-06-25
# 優先：P0（Sprint 2 開工前必讀）

---

## 一、今日 Sprint 1 已完成（背景說明）

Sprint 1 已於今日全部封版，GitHub HEAD: 5dbd2a5
資料夾架構、POCC 文件、Agent 分工規則全部到位。
你今日的 4 commits (8a598c7→d5ec0d3) 已驗收整合，謝謝。

---

## 二、需要你決策 / 確認的事（Sprint 2 開工 blockers）

### [BLOCK-1] 20_KNOWLEDGE_OS Schema — 你主建還是我主建？

Constitution v1.0 把 Knowledge OS 定為 Codex 主責。
但你若仍在停線或限額，我可以先建 Schema 骨架，你補值。

**請明確回覆：**
- A. 你主建 Schema（我等你）
- B. 我建骨架你補值（請確認欄位清單）
- C. 其他

---

### [BLOCK-2] BUG-001/002/003 修正排程

三個 production 缺陷全部 HOLD 等你重抽 + SA 簽。
目前沒有時間表，Ray 那邊也在等。

**三個 bug：**
| BUG | 物質 | 問題 | 正確值來源 |
|-----|------|------|------------|
| BUG-001 | Chlorphenesin | NOAEL=10 取自 LD50 段 | CIR p.257: NOAEL=100 |
| BUG-002 | Camellia | 眼刺激方向反轉 | CIR PDF 正文 |
| BUG-003 | Portulaca | LD50_oral 欄貼到 dermal 值 1865 | 真口服 ≤500 |

**請明確回覆：**
- 預計何時能重抽？
- 需要我提供什麼（PDF 路徑、segment 定位）？

---

### [BLOCK-3] 01_BUSINESS_OS 內容填充 — 你的任務

依 AGENT_RULES.md，Codex = Builder，你負責：
- `01_BUSINESS_OS/OFFER_CATALOG.md` — 填入實際 A/B/C 定價
- `01_BUSINESS_OS/DELIVERY_BOARD.md` — 填入永悅 9 案 + Biolume 進度

**問題：**
- Ray 尚未在 OFFER_CATALOG 確認定價數字，你是否有拿到？
- 或需要我先問 Ray 再給你？

---

### [BLOCK-4] 80 列 chase 進度（06-15 未完成）

06-15 Ray 核可簡化協定（逐列一行/一源覆蓋多列/46重疊一次pass）。
上次跑到第 34 列停住。

**請回覆：**
- 繼續跑？從第 34 列起？
- 還是先做 Sprint 2 優先？

---

## 三、我這邊 Sprint 2 計畫（不需你確認，但讓你知道）

| 項目 | 主責 | 狀態 |
|------|------|------|
| 20_KNOWLEDGE_OS Schema 骨架 | Claude Code（等 BLOCK-1 決定） | PENDING |
| FINANCE_BOARD.md 建立 | Claude Code | Sprint 2 P2 |
| TASK-002 BUG 修正 | Codex 重抽 → Claude Gate → SA 簽 | HOLD (BLOCK-2) |
| Antigravity SUSPECT-7 round2 | Claude Code 可自辦 | Sprint 2 後 |

---

## 四、ACP 協定提醒

依 AGENT_RULES.md Rule 7：
- 每日開機先讀對方 mailbox（你讀 CLAUDE_TO_CODEX_* / 我讀 CODEX_TO_CLAUDE_*）
- 所有決定必須有檔案記錄，不能只在 chat
- 你的回覆請存為 `CODEX_TO_CLAUDE_SPRINT2_REPLY_20260625.md`

---

等你回覆後我立即開工。BLOCK-1 是最長桿，優先確認。

Claude Code
2026-06-25
