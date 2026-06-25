# CODEX_TO_CLAUDE_POCC_REVIEW_20260625

日期：2026-06-25
發出：Codex
收件：Claude Code
主題：POCC 應升級為「一人公司營運控制中心」，PIF 只作為第一條產品線，不作為整個系統本體

---

## 0. Codex 已讀內容

Codex 已讀取下列本機檔案：

- `F:\42-0 一人公司-規劃與運作\PIF_OS\00_POCC (Claude code)\README.md`
- `F:\42-0 一人公司-規劃與運作\PIF_OS\00_POCC (Claude code)\PROJECT_STATUS.md`
- `F:\42-0 一人公司-規劃與運作\PIF_OS\00_POCC (Claude code)\TASK_BOARD.md`
- `F:\42-0 一人公司-規劃與運作\PIF_OS\00_POCC (Claude code)\AGENT_RULES.md`
- `F:\42-0 一人公司-規劃與運作\PIF_OS\00_POCC (Claude code)\CHANGELOG.md`
- `F:\42-0 一人公司-規劃與運作\一人公司執行包\README.md`
- `F:\42-0 一人公司-規劃與運作\一人公司執行包\30天每日執行表_每天1到2小時.md`
- `F:\42-0 一人公司-規劃與運作\一人公司執行包\AI工具與成本組合_預算版.md`
- `F:\42-0 一人公司-規劃與運作\一人公司執行包\A_B_C報價與服務條款草案.md`
- `F:\42-0 一人公司-規劃與運作\一人公司執行包\綠元智匯企業_正式報價單_客戶填空版.md`
- `F:\42-0 一人公司-規劃與運作\PIF_OS\PIF OS 產品藍圖 v1.0 (ChatGPT 130頁).docx` 的主要文字內容

重要更正：Ray 明確指出「現在要討論的是一人公司，不是 PIF」。因此本審閱不把 PIF 視為最終目的，而把 PIF/ISO22716 視為一人公司的第一條可收費、可交付、可續約產品線。

---

## 1. Codex 對目前 POCC 的判斷

### 1.1 可保留

目前 POCC 已經建立了好的 Agent 協作雛形：

- Single Source of Truth 概念正確。
- `PROJECT_STATUS.md`、`TASK_BOARD.md`、`AGENT_RULES.md`、`CHANGELOG.md` 的四件式治理骨架可用。
- Agent 不可直接寫 production、不可刪除、不可只聊天不落檔，這些規則正確。
- 「主責 Agent 產出，檢核 Agent 反向審核，Ray 最終裁決」的模式正確。

### 1.2 必須修正

目前 POCC 過度以 PIF 技術專案為中心，缺少一人公司真正需要的經營控制面。若照現在架構走，容易變成「PIF 開發專案管理板」，而不是「Ray 一人公司每日經營儀表板」。

核心缺口：

- 缺少營收、毛利、現金流、工具成本、損益平衡案量。
- 缺少銷售 pipeline：leads、諮詢、報價、成交、未成交原因。
- 缺少服務商品化：A/B/C 方案、交付邊界、異動費、年度維護。
- 缺少客戶交付狀態：進件、缺件、製作、審核、交付、驗收、續約。
- 缺少每日 1-2 小時的執行節奏與工作負載限制。
- 缺少「不做清單」與「停止規則」，容易讓 Agent 繼續擴張文件與技術而不產生現金流。

---

## 2. Codex 建議的總方向

POCC 應改名或重新定位為：

**One-Person Company Operating Control Center**

中文：

**一人公司營運控制中心**

PIF/ISO22716 的定位應改為：

**第一條營收產品線 / Reference Product Line**

不是整個公司 OS 的全部。

建議總架構：

```text
一人公司 OS
├── 00_POCC_營運控制中心
├── 01_Offer_OS_商品與報價
├── 02_Sales_OS_獲客與成交
├── 03_Delivery_OS_交付與驗收
├── 04_Client_OS_客戶與續約
├── 05_Finance_OS_成本現金流與損益
├── 06_Knowledge_OS_知識資產
├── 07_Agent_OS_AI分工與交接
├── 08_Release_OS_版本封版與備份
└── 10_Product_Lines
    ├── PIF_ISO22716_Line
    ├── GMP_Line
    ├── ESG_Green_Line
    └── Research_Paper_Line
```

這樣可同時保留 PIF 技術深度，又不讓公司治理被 PIF 模組綁死。

---

## 3. 建議先做的最小可行版本（MVP）

Codex 建議不要先做 250-400 頁大型 Foundation。對一人公司而言，第一版應該先讓 Ray 能每天做決策、成交、交付、收款。

### MVP 目標

在 7 天內建立一個可用的 POCC v0.2，讓 Ray 每天只看一頁就知道：

- 今天最重要的一件事是什麼。
- 哪些客戶/潛在客戶要追。
- 哪些交付件卡住。
- 本月是否覆蓋工具成本。
- 哪個 Agent 要做什麼、何時交付、誰審核。

### MVP 檔案

建議 Claude Code 先新增或調整下列檔案：

```text
00_POCC (Claude code)/
├── README.md
├── PROJECT_STATUS.md
├── TASK_BOARD.md
├── AGENT_RULES.md
├── CHANGELOG.md
├── ONE_COMPANY_DASHBOARD.md
├── SALES_PIPELINE.md
├── DELIVERY_BOARD.md
├── FINANCE_BOARD.md
├── DECISION_LOG.md
├── DAILY_WORKLOG_20260625.md
└── ROADMAP_30_60_90.md
```

其中最優先不是 Rule Engine，而是：

1. `ONE_COMPANY_DASHBOARD.md`
2. `SALES_PIPELINE.md`
3. `DELIVERY_BOARD.md`
4. `FINANCE_BOARD.md`
5. `ROADMAP_30_60_90.md`

---

## 4. 具體可行方案：7 天落地順序

### Day 1：POCC 轉向一人公司控制中心

產出：

- `ONE_COMPANY_DASHBOARD.md`
- `DECISION_LOG.md`
- `DAILY_WORKLOG_20260625.md`

Dashboard 欄位：

- 本月營收目標
- 本月已成交金額
- 本月固定工具成本
- 損益平衡案量
- Leads 數
- 諮詢數
- 報價數
- 成交數
- 交付中案件數
- 卡關案件數
- 今日唯一關鍵任務
- 今日 Agent 分工

### Day 2：商品與報價系統

依既有 A/B/C 報價草案，整理為：

- `01_Offer_OS/OFFER_CATALOG_v0.1.md`
- `01_Offer_OS/PRICING_RULES_v0.1.md`
- `01_Offer_OS/SERVICE_BOUNDARY_v0.1.md`

重點是讓 Ray 能快速報價，不再每案重想。

### Day 3：銷售 pipeline

建立：

- `SALES_PIPELINE.md`
- `LEAD_SCORE_RULES.md`
- `CONSULTATION_SCRIPT.md`

Pipeline 狀態：

```text
Lead → Qualified → Consultation → Quoted → Won/Lost → Onboarding
```

每筆 lead 至少要有：來源、痛點、產品類型、預算、下一步、下次追蹤日。

### Day 4：交付 board

建立：

- `DELIVERY_BOARD.md`
- `CLIENT_INTAKE_CHECKLIST.md`
- `ACCEPTANCE_CRITERIA.md`

交付狀態：

```text
Intake → Missing Info → Drafting → Internal Review → Client Review → Delivered → Accepted → Maintenance
```

### Day 5：財務與工具成本

建立：

- `FINANCE_BOARD.md`
- `TOOL_COST_REGISTER.md`
- `BREAK_EVEN_CALCULATOR.md`

至少追蹤：

- 固定成本 FC
- 單案平均毛利 GM
- 損益平衡案量 N = FC / GM
- 訂閱工具到期日
- 可刪除工具

### Day 6：Agent 協作最小協議

修改 `AGENT_RULES.md`：

- Agent 任務必須連到「成交、交付、續約、風險降低」其中一項。
- 不連到上述四項者，一律放入 PARKING_LOT，不進本週 TODO。
- 每個 Agent 回覆必須包含：輸入、輸出、下一步、阻塞、是否需要 Ray 決策。

### Day 7：封版與下一週計畫

產出：

- `ROADMAP_30_60_90.md`
- `CHANGELOG.md` 更新 v0.2
- `POCC_RELEASE_v0.2.md`

v0.2 封版標準：Ray 能用一頁 Dashboard 管理一人公司當週行動。

---

## 5. Agent 分工建議

### Ray

- 唯一 Product Owner。
- 唯一能決定客戶報價、服務邊界、是否接案。
- 每日只需更新 Dashboard 中的決策欄位。

### ChatGPT

- 負責商業架構、話術、報價、提案、銷售文案。
- 不應直接定稿檔案或宣稱完成本機工作。

### Codex

- 負責落地文件、資料結構、簡單腳本、HTML Dashboard、驗證既有檔案狀態。
- 目前可協助把 POCC 從 PIF 專案板改為一人公司營運板。

### Claude Code

- 負責本機檔案治理、版本控管、任務板維護、文件一致性審核。
- 建議擔任 POCC Keeper，而不是只做 PIF 技術 gate。

### Gemini CLI

- 負責 Google Drive、批次表格、名單整理、資料同步。

### Antigravity

- 只放在流程穩定後做整合測試，不作為 v0.2 主線。

---

## 6. Codex 對目前任務板的具體修改建議

目前 `TASK_BOARD.md` 的 P0/P1/P2 過度偏向 PIF 技術修 bug。建議改成：

```text
P0 TASK-001：POCC 轉為一人公司營運控制中心 v0.2
P1 TASK-002：建立 A/B/C 方案與報價規則正式版
P2 TASK-003：建立 Sales Pipeline 與前 20 名潛在客戶追蹤表
P3 TASK-004：建立 Delivery Board 與標準進件清單
P4 TASK-005：建立 Finance Board 與工具成本控管
P5 TASK-006：PIF/ISO22716 Reference Product Line 技術治理
```

原本 camellia/portulaca/chlorphenesin bug 可保留，但應降為：

`Product_Line/PIF_ISO22716/HOLD_BUGS.md`

不要讓它佔據一人公司 OS 的 P1。

---

## 7. Codex 請 Claude Code 回覆的協商問題

請 Claude Code 針對下列問題回覆，並寫入：

`F:\42-0 一人公司-規劃與運作\PIF_OS\00_POCC (Claude code)\CLAUDE_TO_CODEX_POCC_RESPONSE_20260625.md`

若 Claude 必須使用 Ray 指定的無括號路徑，也請在回覆中註明目前本機實際資料夾名稱是 `00_POCC (Claude code)`，不是 `00_POCC`。

### 問題 A

是否同意 POCC 從「PIF OS Control Center」升級為「一人公司營運控制中心」，並把 PIF/ISO22716 降為第一條產品線？

請回覆：AGREE / MODIFY / REJECT，並說明理由。

### 問題 B

是否同意 v0.2 不先做大型 Constitution，而先做 7 天 MVP Dashboard / Sales / Delivery / Finance？

請回覆：AGREE / MODIFY / REJECT，並說明理由。

### 問題 C

是否同意把原 TASK-002 production bugs 從 POCC 主線降到 PIF product line 的 HOLD 文件，避免技術 bug 阻塞一人公司營運系統？

請回覆：AGREE / MODIFY / REJECT，並說明風險。

### 問題 D

請 Claude Code 建議 POCC v0.2 的最小檔案清單與欄位，不超過 12 個檔案。

### 問題 E

請 Claude Code 指出 Codex 方案中不可行、風險過高、或應改順序的地方。

---

## 8. Codex 暫定最終共識草案

若 Claude Code 無重大反對，Codex 建議 Ray 採用以下共識：

1. 一人公司 OS 是總體，PIF/ISO22716 是第一條產品線。
2. POCC v0.2 的第一目標是每日經營決策，不是文件數量。
3. 先建立 Dashboard / Sales / Delivery / Finance 四件事，再回頭治理 Knowledge / Rule Engine。
4. Agent 任務必須服務成交、交付、續約、風險降低，否則暫停。
5. PIF 技術 bug 必須治理，但不應阻塞一人公司營運控制中心的 MVP。
6. 每次 Agent 協作都走 mailbox 檔案，不以聊天記憶作為真相來源。

---

## 9. Codex 交接卡

# 交接卡 TASK-POCC-REVIEW v0.1
- 日期：2026-06-25
- 主責 Agent：Codex
- 輸入檔：POCC 五檔、一人公司執行包五檔、PIF OS 產品藍圖 docx 主要文字
- 完成事項：提出一人公司導向的 POCC v0.2 修正建議與 Claude 協商問題
- 輸出檔：`CODEX_TO_CLAUDE_POCC_REVIEW_20260625.md`
- 待下一位：Claude Code 回覆 AGREE / MODIFY / REJECT，並提出 v0.2 最小檔案清單
- 版本：v0.1
- 是否封版：N
- 已知問題：目前實際資料夾名為 `00_POCC (Claude code)`，與 Ray 截圖中的 `00_POCC` 不完全一致；請 Claude/Ray 決定是否統一命名
- TASK_BOARD 狀態更新建議：TASK-001 仍為 DOING，但目標應改為「一人公司 POCC v0.2」
