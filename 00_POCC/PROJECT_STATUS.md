# PIF OS — PROJECT STATUS
> **Single Source of Truth（唯一真相來源）**
> 每日由主責 Agent 更新。所有 Agent 開始工作前必讀此檔。

---

## 最後更新
- 日期：2026-06-25
- 更新者：Claude Code
- 版本：v0.1

---

## 系統完成度總覽

| 子系統 | 完成度 | 狀態 | 備註 |
|--------|--------|------|------|
| PIF 生成引擎（Document OS） | ~70% | 🟡 進行中 | 架構完整，Rule Engine 尚未建置 |
| 法規知識庫（Regulatory KB） | ~50% | 🟡 進行中 | 台灣法規已建，多國/AI判讀尚未 |
| 原料知識庫（Ingredient KB） | ~40% | 🔴 缺口大 | NOAEL/LD50 端點有已知 production bug |
| 功效知識庫（Efficacy KB） | ~20% | 🔴 未啟動 | 欄位定義中 |
| 文件管理系統（Document Management） | ~30% | 🔴 缺口大 | 版控/自動歸檔未建 |
| Agent 協作平台（POCC） | ~5% | 🟡 本週啟動 | 本批三檔為第一版 |

---

## 本週最高優先任務（Top 3）

| 優先序 | Task ID | 任務描述 | 負責 Agent | 狀態 |
|--------|---------|----------|------------|------|
| P0 | TASK-001 | 建立 POCC 基礎結構（本批三檔） | Claude Code | ✅ 進行中 |
| P1 | TASK-002 | camellia + portulaca production bug 修正（等 Codex 6/21+ SA 簽） | Codex + SA | 🔴 HOLD - 等 Codex 回線 |
| P2 | TASK-003 | PIF + ISO22716 知識庫欄位定義（Schema 先行） | Claude Code → Codex | 🟡 待開始 |

---

## 已知重大缺陷（Production Bugs）

| Bug ID | 物質 | 問題 | 狀態 |
|--------|------|------|------|
| BUG-001 | Chlorphenesin | noael=10 取自 LD50 段，非 NOAEL | HOLD - 等 Codex + SA |
| BUG-002 | Camellia | 眼刺激方向反轉（Non-irritant → Slight ocular irritant） | HOLD - 等 Codex + SA |
| BUG-003 | Portulaca | LD50 oral 欄位誤貼 dermal 值 | HOLD - 等 Codex + SA |

> ⚠️ 以上三個 bug **嚴禁在 SA 簽核前 promote 至 production**。

---

## 各 Agent 目前狀態

| Agent | 在線狀態 | 上次活躍 | 目前分工 |
|-------|----------|----------|----------|
| Claude Code（本工具） | ✅ 在線 | 2026-06-25 | 執行主力、品質把關、POCC 建置 |
| Codex（OpenAI） | 🔴 停線中 | 2026-06-06 | 知識庫填充、端點爬取 |
| ChatGPT | 🟡 非同步 | 2026-06-25 | 策略規劃（本文件來源） |
| Gemini CLI | ⬜ 待啟用 | — | 批次資料、Google 系統 |
| GitHub Education | ✅ 可用 | — | 版本控管 |
| Antigravity | 🟡 外援 | 2026-06-19 | CIR 端點草稿（非正式） |

---

## 系統架構（確定版）

```
Layer 0 — Project OS (POCC)
    ↓
Layer 1 — Knowledge OS（法規 KB / 原料 KB / 功效 KB）
    ↓
Layer 2 — Document OS（PIF / ISO22716）
    ↓
Layer 3 — Automation OS（Rule Engine / AI / 版控 / 稽核）
```

> 開發優先順序：先把 **PIF + ISO22716** 做成 Reference Implementation，再複製到 GMP、ESG、綠色無毒。

---

## 下次開工前必做

1. 讀本檔（PROJECT_STATUS.md）確認最新狀態
2. 讀 TASK_BOARD.md 確認任務分派
3. 讀 AGENT_RULES.md 確認工作規範
4. 讀 CODEX_TO_CLAUDE_* mailbox（如有新訊息）
