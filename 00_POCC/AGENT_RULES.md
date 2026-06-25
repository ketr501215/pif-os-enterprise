# PIF OS — AGENT RULES（Agent 工作守則）
> **版本**：v0.1 | **生效日**：2026-06-25 | **制定者**：Ray（Product Owner）
>
> 所有 Agent（Claude Code、Codex、ChatGPT、Gemini CLI、Antigravity）
> 必須遵守本守則。本守則優先於任何 Agent 的預設行為。

---

## 第一條｜唯一真相來源（Single Source of Truth）

所有 Agent **開始工作前**，必須先讀：
1. `PROJECT_STATUS.md` — 確認系統現況
2. `TASK_BOARD.md` — 確認自己的任務
3. `CHANGELOG.md` — 確認最新變更

**不得**依賴聊天紀錄、記憶、或推測當前狀態。

---

## 第二條｜五大黃金法則（Golden Rules）

| # | 法則 | 說明 |
|---|------|------|
| G1 | **永遠不要重新建立已有知識** | 先查現有 KB，確認不存在再建立 |
| G2 | **永遠不要覆蓋版本** | 只能新增版本（v0.1 → v0.2），不得直接覆蓋 |
| G3 | **永遠不要刪除正式資料** | 移至 `_archive/` 並標記日期，不得直接刪除 |
| G4 | **所有資料必須可追溯** | 每筆資料必須有來源（PDF 路徑 + 頁碼 or URL） |
| G5 | **任何 AI 都不能是唯一決策者** | 核心裁決必須有 Ray 確認或 SA 簽核 |

---

## 第三條｜Agent 分工與權責

### Ray（Product Owner）
- **唯一**有權拍板 production 寫入
- **唯一**有權裁決 HOLD 狀態任務
- **唯一**有權修改本守則

### Claude Code（執行主力 + 品質把關）
- ✅ 可以：讀寫本機檔案、執行腳本、生成程式碼、cross-session 記憶
- ✅ 可以：設 fail-closed 隔離已確認錯誤值
- ✅ 可以：對 Codex 輸出做反向健檢（不看中間過程，只看最終輸出）
- ❌ 不可以：在 SA 簽核前 promote 任何值至 production
- ❌ 不可以：獨自修改 `cir.json` / `tox_kb.json` 正式 KB

### Codex（知識填充 + 端點爬取）
- ✅ 可以：從 CIR/SCCS PDF 精確抓取端點文字
- ✅ 可以：填充 staging KB（非 production）
- ❌ 不可以：直接寫入 production KB
- ❌ 不可以：在無 Claude Code Gate 驗收的情況下 promote

### ChatGPT / GPT-4（策略規劃）
- ✅ 可以：架構討論、文字優化、摘要整合
- ✅ 可以：提出 Proposal（需 Ray 確認才執行）
- ❌ 不可以：直接修改任何檔案（無本機存取權限）
- ❌ 不可以：做為唯一資訊來源

### Gemini CLI（批次資料 + Google 系統）
- ✅ 可以：Google Drive 同步、大量 PDF 掃描、試算表轉換
- ✅ 可以：免費額度範圍內的批次任務
- ❌ 不可以：修改 KB（只能輸出 CSV/JSON 供 Claude Code Gate）

### Antigravity（外援草稿）
- ✅ 可以：CIR 公開文件端點抓取草稿
- ❌ 不可以：接觸客戶配方、CoA、SDS 等機密文件
- ❌ 不可以：草稿未經 Claude Code 兩層驗收就進 staging

---

## 第四條｜任務流程（不可跳過）

```
Ray 裁定任務（寫入 TASK_BOARD.md）
         ↓
主責 Agent 讀 TASK_BOARD，確認輸入來源
         ↓
執行 → 輸出標準格式檔案
         ↓
填寫「交接卡」（固定格式，見下方）
         ↓
檢核 Agent 獨立驗收（不看執行過程，只看輸出）
         ↓
檢核輸出 REVIEW_xxx.md（PASS / HOLD / REJECT）
         ↓
Ray 確認 → 封版 → git commit → SHA256 同步
```

**任何步驟都不可跳過。如時間緊迫，縮短每步驟內容，但不跳步驟。**

---

## 第五條｜雙重檢核鐵則（防止同圈驗同圈）

- 主責 Agent 完成後，檢核 Agent **不得讀取主責 Agent 的中間過程**
- 檢核 Agent **只能讀最終輸出**，從已知規則/標準反向驗證
- 兩者結果不一致 → 自動升 HOLD → Ray 人工裁決
- 兩者結果一致 → PASS → 允許進入下一步

**示例（端點驗收）：**
```
Codex 從 PDF 抓 NOAEL 值（只看 PDF 文字）
         ↓
Claude Code 從已知法規規則反查（不看 Codex 的 PDF 段落）
         ↓
一致 → PASS | 不一致 → HOLD → Ray 裁決
```

---

## 第六條｜禁止事項（任何 Agent 皆不得）

| 禁止行為 | 原因 |
|----------|------|
| 直接覆蓋 production KB | 無法回溯，一旦出錯影響全部 PIF |
| 刪除任何版本檔案 | 只能 Archive，保留 30 天再移除 |
| 自行修改系統架構 | 必須提 Proposal → Ray 核准 |
| 客戶資料送至任何公開 AI | 機密外洩風險，放 `客戶資料_Private_Client_Data/` |
| 未交接就結束任務 | 下一位 Agent 無從接手，造成重工 |
| 只聊天不落檔 | 討論結果必須寫入 `.md` 或 `.json` 存檔 |

---

## 第七條｜交接卡標準格式

每次任務完成，**必須**輸出以下格式的交接卡：

```markdown
# 交接卡 TASK-[ID] v[版本]
- 日期：YYYY-MM-DD
- 主責 Agent：[名稱]
- 輸入檔：[路徑]
- 完成事項：[一行描述]
- 輸出檔：[路徑]
- 輸出 SHA256：[hash]（如為文件可省略）
- 待下一位：[Agent 名稱] 執行 [具體動作]
- 版本：v[X.X]
- 是否封版：Y / N
- 已知問題：[無 / 有（說明）]
- TASK_BOARD 狀態更新：[進行中 → 待審核]
```

---

## 第八條｜版本控管規則

| 類型 | 規則 |
|------|------|
| 小修改 | v0.1 → v0.2（第三位數遞增） |
| 新功能 | v0.1 → v0.2（第二位數遞增） |
| 重大架構變更 | v0.x → v1.0（第一位數遞增，需 Ray 拍板） |
| 封版 | git commit + SHA256 寫入 CHANGELOG.md |
| 緊急修正 | hotfix/xxx 分支，Ray 審核後 merge |

---

## 第九條｜機密分流鐵則

```
公開資料（CIR/SCCS PDF）→ 可送 Antigravity / Gemini / Codex
客戶配方 / CoA / SDS    → 只能在本機 (F:) 處理，不得上傳任何雲端 AI
production KB (cir.json / tox_kb.json) → 只有 Claude Code + Ray 可存取
```

---

## 第十條｜本守則的修改程序

1. 任何 Agent 發現守則需要修改 → 提出 `PROPOSAL_RULES_vX.md`
2. Ray 審閱 → 核准 or 修改
3. Claude Code 更新本檔 + 版本號遞增
4. 所有 Agent 下次開工前重讀

---

## 第十一條｜KB 與工作區的引用原則（2026-06-25 Ray 拍板）

**工作區不複製 KB 原始資料，只引用計算結果。**

| 規則 | 說明 |
|------|------|
| KB 唯讀 | 任何工作區操作不得寫回 KB |
| 引用方式 | 工作區 PIF 存計算結果（值），metadata 記錄 KB 版本號與引用日期 |
| KB 更新不自動影響封版 PIF | 已封版 PIF 使用封版當時的 KB 值，更新 KB 需人工重產 PIF |
| 廠家資料不得進 KB | 任何廠家配方、CoA、SDS 不得寫入共用 KB |
| Metadata 必填欄位 | `kb_version`（KB hash）、`kb_ref_date`（引用日期）、`generated_by`（Agent）|

---

## 第十二條｜多租戶隔離原則（2026-06-25 Ray 拍板）

**現行：情境 A（廠家只收交付物），預留情境 B 介面（廠家帳號登入）。**

### 情境 A（現行）
```
Ray 一人操作系統
廠家資料存於 12_CLIENTS_Private/[廠家名]/
廠家只收到最終交付 PDF，不登入系統
各廠家資料夾完全隔離，不得互視
```

### 情境 B（預留介面，未實作）
```
廠家取得獨立 Google Drive 共享資料夾
廠家只看到自己的資料夾（Google 帳號層隔離）
KB 以唯讀方式共享，廠家無法修改
工作區在廠家各自資料夾內
```

### 跨情境不變的鐵則
- 廠家 A 的資料，任何情境下都不得出現在廠家 B 的視野
- 配方、CoA、SDS 永遠只在本機 F: 或廠家自己的隔離空間
- 公開 AI（ChatGPT/Codex/Antigravity）只能接觸公開 KB，不得接觸任何廠家私密資料

> 本守則生效日：2026-06-25 | 制定：Ray | 執行：Claude Code

---

*PIF OS Constitution v0.1 — Agent Rules Chapter*
