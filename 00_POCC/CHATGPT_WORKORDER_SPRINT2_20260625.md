# CHATGPT_WORKORDER_SPRINT2_20260625.md
# 寄件：Claude Code（代 Ray 分派）
# 收件：ChatGPT（Chief Architect + PMO 角色）
# 日期：2026-06-25
# 背景：考量 Claude Code 額度，將架構審閱與 Business OS 工作移交

---

## 0. 背景說明（你需要知道的）

PIF OS Enterprise 是一個一人公司 AI Operating System。
你（ChatGPT）在 6/24 已完成 130 頁產品藍圖，是這個系統的 Chief Architect。

現在 Sprint 2 開始：
- Codex 負責建 Knowledge OS Schema（04_KNOWLEDGE_OS/）
- Claude Code 負責 production tox 安全把關
- **你負責 PMO + 架構審閱 + Business OS**

GitHub repo（唯讀參考）：https://github.com/ketr501215/pif-os-enterprise
⚠️ 客戶資料不在 repo，配方/CoA/SDS 永不上傳

---

## 1. Gate Review 任務（等 Codex 交付後執行）

### [GATE-1] Knowledge OS Schema 審閱
Codex 即將交付以下 4 份文件到 `04_KNOWLEDGE_OS/`：
- `SCHEMA_v0.1.md`
- `SOURCE_REGISTRY_v0.1.md`
- `REGULATORY_KB_SCHEMA_v0.1.md`
- `INGREDIENT_KB_SCHEMA_v0.1.md`

**你的 Gate 檢核點：**
1. 每個 knowledge record 是否有 `source / provenance / version` 欄位？
2. 是否符合 Constitution 的「no duplicate knowledge」規則（同一知識只存一處）？
3. Schema 是否能支援後續 Document OS（30_DOCUMENT_OS）與 Rule Engine（06_RULE_ENGINE）？
4. 命名與 Constitution v1.0 的術語是否一致？

**輸出：** `00_POCC/CHATGPT_TO_CLAUDE_SCHEMA_GATE_20260625.md`（PASS / CONDITIONAL / FAIL）

---

### [GATE-2] MASTER_BLUEPRINT_INDEX 審閱
Codex 即將交付 `03_MASTER_BLUEPRINT/MASTER_BLUEPRINT_INDEX_v0.1.md`

**你的 Gate 檢核點：**
1. 是否涵蓋所有頂層文件（Constitution / ADR001 / 產品藍圖 / POCC）？
2. 是否有清晰的 Single Source of Truth 指向（每個主題只有一個權威文件）？
3. 是否符合你在產品藍圖中設計的 4 層架構（OS / Knowledge / Document / Automation）？

**輸出：** 同上 gate 文件，附加 Blueprint Index 審閱意見

---

### [GATE-3] AGENT_HANDOFF_PROTOCOL 審閱
Claude Code 已建立 `08_AGENT_OS/AGENT_HANDOFF_PROTOCOL_v0.1.md`

**你的 Gate 檢核點：**
1. Mailbox 命名規則是否清晰、不易混淆？
2. 每日開機 SOP 6 步驟是否合理？
3. 交接卡格式是否完整（輸入/輸出/待辦/封版）？
4. 雙重檢核規則是否能阻斷同圈驗證問題？

**輸出：** 同上 gate 文件，附加 Protocol 審閱意見

---

## 2. Business OS 任務（你直接建立）

### [BIZ-1] OFFER_CATALOG 填充
現有骨架：`01_BUSINESS_OS/OFFER_CATALOG.md`（空骨架，Codex 建立）

**請填入：**
- A 方案（入門版）：適合對象、交付內容、定價 range
- B 方案（專業版）：4A 色階 MoS、適合對象、定價 range
- C 方案（企業版）：完整 ISO22716 審計、適合對象、定價 range

⚠️ 定價用 range（不寫死），Ray 最終確認
⚠️ 不得包含客戶姓名或真實合約金額

---

### [BIZ-2] DELIVERY_BOARD 填充
現有骨架：`01_BUSINESS_OS/DELIVERY_BOARD.md`

**請填入（匿名化）：**
- 永悅：9 案，PIF+ISO22716，待 SA 簽核
- Biolume：1 案，完整版 207 頁，待 SA 簽核
- 進度欄位：草稿 / Gate PASS / SA 簽核 / 交付

---

### [BIZ-3] FINANCE_BOARD 新建
路徑：`01_BUSINESS_OS/FINANCE_BOARD.md`

**請建立：**
- 工具成本試算（Claude Code / Codex / ChatGPT / Gemini CLI 各訂閱費）
- 人月估算（Ray 一人，每週工時估算）
- 損益平衡：幾個案子可回收工具成本？
- 下一個 25 案的試算

---

## 3. 輸出規範

- 所有文件存入對應資料夾（`01_BUSINESS_OS/` 或 `00_POCC/`）
- Gate review 用 CHATGPT_TO_CLAUDE_* 命名
- Business OS 文件直接存到 `01_BUSINESS_OS/`
- ⚠️ 不得包含客戶真實資料、配方、CoA、合約金額

---

## 4. 不需要你做的（Claude Code 保留）

- BUG-001/002/003 生產修正
- git commit / push
- production tox 資料庫操作

---

謝謝，等你的交付。
Claude Code（代 Ray）
2026-06-25
