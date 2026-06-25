# NEXT_BOOT_HANDOFF_20260626.md
# 給下次開機的自己（Claude Code）與所有 Agent
# 撰寫：Claude Code | 日期：2026-06-25 EOD
# GitHub HEAD：ce63387

---

## 開機 SOP（照順序，不跳）

```
Step 1  git pull
Step 2  讀本檔（NEXT_BOOT_HANDOFF_20260626.md）
Step 3  讀 08_AGENT_OS/Claude/STATUS.md
Step 4  讀 09_PROJECT_OS/DAILY_BROADCAST_20260625.md
Step 5  看各 Agent STATUS.md（Codex 有無交付 Schema？）
Step 6  開工
```

---

## 第一件事：確認 Codex 是否已交付

```
F:\42-0 一人公司-規劃與運作\PIF_OS\04_KNOWLEDGE_OS\SCHEMA_v0.1.md
```

- 有 → 立刻 Gate Review（只讀最終輸出，記錄於 09_PROJECT_OS/REVIEW/）
- 無 → 更新 Claude STATUS.md Waiting 欄，繼續等

---

## 明日優先任務

| 優先 | 任務 | 主責 | 輸出 |
|------|------|------|------|
| P0 | KB Schema Gate Review | Claude Code | `09_PROJECT_OS/REVIEW/KB_SCHEMA_REVIEW.md` |
| P0 | Codex 交付 SCHEMA_v0.1.md | Codex | `04_KNOWLEDGE_OS/SCHEMA_v0.1.md` |
| P1 | Business OS 定價填充 | ChatGPT | 等 Ray 確認定價欄位 |
| P1 | Google Drive Mirror 驗證 | Gemini/Claude | F: ↔ Google Drive SHA |
| P2 | NOTE-2 裁決 | Ray | 是否補備份分類條文 |

---

## 系統狀態（接班點）

```
GitHub:  Public repo ce63387
         https://github.com/ketr501215/pif-os-enterprise

Constitution: v1.2（02_CONSTITUTION/PIF_OS_Constitution_v1.2.md）
AGENT_RULES:  第1～13條（含 KB引用/多租戶/日報制度）

Production KB: 未動（719FDE0E / 59CE6888）
BUG-001/002/003: HOLD（等 Codex 重抽 + SA）

工作流程:
  - 各 Agent 只看 STATUS.md，不寄信
  - 工作包在 09_PROJECT_OS/WORK_PACKAGE/
  - Review 在 09_PROJECT_OS/REVIEW/
  - 決策在 00_POCC/DECISION_LOG.md
```

---

## 待 Ray 明日確認

1. **OFFER_CATALOG 定價欄位**：哪些可公開？寫入 repo？
2. **NOTE-2**：AGENT_RULES 補「三種備份分類」細則？
3. **Google Drive**：指派 Gemini 做驗證？還是手動？
4. **BUG 修正序**：SA 什麼時候可以排 BUG-001/002/003 簽核？

---

## 不要做的事（開機提醒）

- ❌ 不要寄 mailbox 信件（改看 STATUS.md）
- ❌ 不要動 production KB（BUG 仍 HOLD）
- ❌ 不要在 chatGPT Gate Review 前 promote 任何 Schema
- ❌ 不要把客戶資料 commit 到 git

---

Claude Code
2026-06-25 EOD | 下次接班：2026-06-26
