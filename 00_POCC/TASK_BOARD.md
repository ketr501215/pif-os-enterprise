# PIF OS — TASK BOARD
> 所有 Agent 只讀此板，不讀聊天紀錄。
> 狀態：🔴 待開始 | 🟡 進行中 | 🔵 待審核 | ✅ 完成 | ⛔ HOLD

---

## 看板總覽

```
待開始(TODO) → 進行中(DOING) → 待審核(REVIEW) → 完成(DONE)
```

---

## ⛔ HOLD（等外部條件）

### TASK-002 | camellia + portulaca production 修正
- **目的**：修正已知三個 production bug（BUG-001/002/003）
- **輸入**：
  - `F:\11-7...\DATApool_2_regulatory_staging\` Codex 重抽結果
  - SA 簽核裁決單
- **預期輸出**：更新後 `cir.json`（hash 變更）+ SA 蓋章
- **主責 Agent**：Codex（重抽）→ Claude Code（gate 驗收）→ SA（簽核）→ Ray（拍板）
- **檢核 Agent**：Claude Code 反向健檢（不看 Codex 原始段落）
- **卡住原因**：Codex 停線（上次回應 2026-06-06）
- **解鎖條件**：Codex 回線 + SA 排程
- **版本**：v0.0（未啟動）

---

## 🟡 進行中（DOING）

### TASK-001 | POCC 基礎結構建置
- **目的**：建立所有 Agent 共用的 Shared Workspace 入口
- **輸入**：PIF OS 產品藍圖 v1.0 (2026 0625).docx（Ray 提供）
- **預期輸出**：
  - ✅ `PROJECT_STATUS.md`
  - ✅ `TASK_BOARD.md`（本檔）
  - ✅ `AGENT_RULES.md`
  - 🔴 `CHANGELOG.md`（下一步）
  - 🔴 `ROADMAP.md`（下一步）
- **主責 Agent**：Claude Code
- **檢核 Agent**：Ray 確認後封版
- **版本**：v0.1
- **備註**：本批三檔為 Sprint 1 Day 1 產出

---

## 🔴 待開始（TODO）

### TASK-003 | PIF + ISO22716 欄位定義（Schema 先行）
- **目的**：在爬蟲/AI 填資料之前，先定義系統「需要哪些欄位」
- **輸入**：現有 `cir.json` 欄位結構 + PIF 1-16 架構
- **預期輸出**：
  - `Knowledge_OS/ingredient_schema_v1.json`（原料 KB schema）
  - `Document_OS/pif_field_mapping_v1.md`（PIF 欄位對照）
- **主責 Agent**：Claude Code
- **檢核 Agent**：Codex（回線後驗證欄位完整性）
- **前置條件**：TASK-001 完成
- **預估工時**：2-3 小時
- **版本**：v0.0（未啟動）

### TASK-004 | Antigravity 待處理批次（SUSPECT 7 筆裁決）
- **目的**：對 adjudication_v3_20260619.json 中 SUSPECT=7 筆做最終裁決
- **輸入**：`_returned/adjudication_v3_20260619.json`（SUSPECT 7 筆）
- **預期輸出**：裁決結果（round-3 重送 or 人工定值）
- **主責 Agent**：Ray 裁決方向 → Claude Code 執行
- **前置條件**：Ray 確認處理方式
- **版本**：v0.0（未啟動）

### TASK-005 | Rule Engine 設計（PIF 法規規則引擎）
- **目的**：實作 `IF 產品類型=美白 THEN 需檢查功效試驗+安全評估+標示` 邏輯
- **輸入**：台灣化粧品法規 + PIF 規範
- **預期輸出**：`Rule_Engine/pif_rules_v1.json`
- **主責 Agent**：Claude Code（設計）→ Codex（驗證）
- **前置條件**：TASK-003 完成
- **版本**：v0.0（未啟動）

### TASK-006 | Agent Control Center HTML（POCC 視覺化介面）
- **目的**：建立 `PIF_OS_Control_Center_v0.1.html` 讓 Ray 一頁掌握全系統狀態
- **輸入**：本 TASK_BOARD.md + PROJECT_STATUS.md
- **預期輸出**：單機 HTML 儀表板
- **主責 Agent**：Claude Code
- **前置條件**：TASK-001 完成
- **版本**：v0.0（未啟動）

---

## ✅ 完成（DONE）

### TASK-000 | PIF OS 策略規劃討論
- **完成日**：2026-06-25
- **輸出**：`PIF OS 產品藍圖 v1.0 (2026 0625).docx`
- **主責 Agent**：ChatGPT（規劃）
- **版本**：v1.0 封版

---

## 交接卡模板（每次交接必填，貼在對話最頂端）

```markdown
# 交接卡 TASK-[ID]
- 輸入檔：[路徑]
- 完成：[做了什麼，一行說明]
- 輸出：[路徑] SHA256=[hash]
- 待下一位：[Agent 名稱] 做 [具體動作]
- 版本：v[X.X]
- 是否封版：Y/N
- 已知問題：[有/無，若有請說明]
```
