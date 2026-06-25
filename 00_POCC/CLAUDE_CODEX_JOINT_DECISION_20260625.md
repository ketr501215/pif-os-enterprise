# Claude Code × Codex 聯合協商決議
# PIF OS Enterprise — Sprint 1 分工、GitHub、架構確認

日期：2026-06-25
發出：Claude Code（代表雙方整合，送 Ray 核可）
依據：ADR001 + Constitution v1.0 (Gemini) + Codex v0.2 + Claude Response

---

## 一、今日三大決策確認（來自 Constitution p.5）

| ID | 決策 | 狀態 |
|----|------|------|
| D001 | 專案策略收斂為「先核心 PIF + ISO22716 系統驗證，其餘模組比照 Plugin 掛載」 | ✅ Ray 核可 |
| D002 | ACP 檔案級交接協議 + 雙重檢核機制，徹底阻斷 Agent 聊天重工成本 | ✅ 已建入 AGENT_RULES.md |
| D003 | F 槽為最高 Master，Google Drive ketr501218 為 Mirror，版本遞增規則建立 | ✅ 待 SYNC_STATUS.md 實證 |

---

## 二、資料夾架構（確定版，今日完成命名）

```
F:\42-0 一人公司-規劃與運作\PIF_OS\          ← Master 根目錄
│
├── 00_POCC\                                  ← ✅ 已改名（原 00_POCC (Claude code)）
│   ├── README.md
│   ├── PROJECT_STATUS.md
│   ├── TASK_BOARD.md
│   ├── AGENT_RULES.md
│   ├── CHANGELOG.md
│   ├── EXECUTIVE_DASHBOARD.md               ← 🔴 下次開機第一件事（Claude Code）
│   ├── DECISION_LOG.md                      ← 🔴 下次開機（Claude Code）
│   ├── RISK_REGISTER.md                     ← 🔴 下次開機（Claude Code）
│   ├── SYNC_STATUS.md                       ← 🔴 下次開機（Claude Code）
│   ├── WORKLOG_20260625.md                  ← 🔴 本次收工前（Claude Code）
│   └── RELEASE_GATE.md                      ← Sprint 2
│
├── 01_BUSINESS_OS\                           ← 🔴 Sprint 1（Codex 主建）
│   ├── OFFER_CATALOG.md
│   └── DELIVERY_BOARD.md
│
├── 10_PRODUCT_LINES\
│   └── PIF_ISO22716\                         ← 🔴 Sprint 1（Claude Code 主建）
│       ├── PRODUCT_STATUS.md
│       ├── HOLD_BUGS.md
│       └── ACCEPTANCE_CRITERIA.md
│
├── 20_KNOWLEDGE_OS\                          ← Sprint 2
├── 30_DOCUMENT_OS\                           ← Sprint 2
├── 40_RULE_ENGINE\                           ← Sprint 3
├── 50_AGENT_OS\                              ← 持續維護
└── 99_ARCHIVE\                               ← 永久保留
```

---

## 三、GitHub 安全備份計畫

### Repo 名稱（確定）
```
pif-os-enterprise   （Private）
```

### 三層同步架構
```
F:\42-0 一人公司-規劃與運作\PIF_OS\   ← Master（本機，最高權威）
         ↓ robocopy / manual sync
Google Drive ketr501218\PIF_OS\       ← Mirror（雲端鏡像，每日同步）
         ↓ git push
GitHub Private: pif-os-enterprise     ← Version Control（封版才推）
```

### GitHub 要排除的內容（.gitignore）
```gitignore
# 客戶機密
客戶資料_Private_Client_Data/
**/CoA/
**/SDS/
**/*配方*

# 大型二進位
*.pdf
*.docx
*.xlsx
*.zip

# 系統暫存
.DS_Store
Thumbs.db
~$*
```

### GitHub 推送時機（不是每天推）
- 每次 Work Package 完成封版 → git commit + git push
- 重大決策後 → 立即 commit DECISION_LOG.md
- 每週五固定全量 push

### 第一次 GitHub 初始化步驟（下次開機執行）
```powershell
cd "F:\42-0 一人公司-規劃與運作\PIF_OS"
git init
git remote add origin https://github.com/[Ray帳號]/pif-os-enterprise.git
git add 00_POCC\
git commit -m "feat: POCC v0.1 Sprint 1 - foundation files"
git push -u origin main
```
> ⚠️ 需 Ray 提供 GitHub 帳號或確認是否已建立 Private Repo

---

## 四、Agent 分工（最終確定版）

| Agent | 角色 | 主要工作 | 可執行 Sprint |
|-------|------|----------|--------------|
| **Ray** | Product Owner | 裁決、拍板、SA 協調 | 全程 |
| **Claude Code** | Reviewer + Executor | POCC 建置、品質 Gate、cross-session 記憶 | Sprint 1+ |
| **Codex** | Builder | Knowledge 填充、Business OS、端點爬取 | Sprint 1+（回線後） |
| **ChatGPT** | Chief Architect + PMO | 策略討論、規劃文件 | 已完成藍圖 |
| **Gemini CLI** | Knowledge + Batch | Google 系統、批次 PDF 處理 | Sprint 2+ |
| **Antigravity** | Integration Test | CIR 草稿驗收、整合測試 | Sprint 3+ |

### 雙重檢核對應表
| 主責 | 檢核 | 觸發條件 |
|------|------|----------|
| Codex（知識填充）| Claude Code（Gate）| 每次 staging 更新 |
| Claude Code（POCC 文件）| Codex（內容審閱）| 每次 Work Package 完成 |
| Claude Code（程式邏輯）| Ray（最終拍板）| production promote 前 |

---

## 五、第一個馬上需建立的架構（下次開機第一優先）

### WP-001：EXECUTIVE_DASHBOARD.md（優先序 P0）

**為什麼這個最優先：**
- Ray 每天開機第一眼需要看到「今天最重要的一件事 + 系統風險狀態」
- 沒有這個，所有 Agent 都不知道公司層的優先序
- Constitution p.1 也把 EXECUTIVE DASHBOARD 列為 POCC 最頂層

**內容（固定 6 個區塊）：**
```markdown
## 今日唯一關鍵任務
## 本週里程碑與完成率（只計實際封版檔案）
## 系統風險（RED/YELLOW/GREEN）
## 需 Ray 決策的事項
## 阻塞事項（Blocked）
## 同步狀態（F ↔ Google ↔ GitHub）
```

**主責：** Claude Code  
**預估：** 30 分鐘  
**驗收：** Ray 能在 30 秒內讀完並知道今日該做什麼

---

## 六、下次開機銜接 SOP（收工前確認清單）

```
□ 1. 讀 00_POCC/EXECUTIVE_DASHBOARD.md（第一眼）
□ 2. 讀 00_POCC/TASK_BOARD.md（確認自己任務）
□ 3. 讀 mailbox（00_POCC/ 內 CODEX_TO_CLAUDE_* 或 CLAUDE_TO_CODEX_*）
□ 4. 確認 SYNC_STATUS.md（F ↔ Google ↔ GitHub 是否一致）
□ 5. 開始執行最高優先任務
```

---

## 七、交接卡（今日 Session 收工）

```
# 交接卡 SPRINT-1 DAY-1 v0.1
- 日期：2026-06-25
- 主責：Claude Code
- 輸入：ADR001 + Constitution v1.0 (Gemini) + Codex v0.2 + Claude Response
- 完成：
  ✅ 00_POCC 資料夾改名（移除 "(Claude code)"）
  ✅ 8 個 POCC 基礎檔案建立
  ✅ Claude × Codex 協商完成（6 點共識）
  ✅ 架構確定（7 層資料夾）
  ✅ GitHub 計畫確定（pif-os-enterprise, Private）
  ✅ 本聯合決議檔建立
- 輸出：本檔 + WORKLOG_20260625.md（待建）
- 待下一位：
  Ray → 確認 GitHub 帳號 / 建立 Private Repo
  Claude Code（下次開機）→ 建 EXECUTIVE_DASHBOARD.md（P0）
  Codex（回線後）→ 建 01_BUSINESS_OS/OFFER_CATALOG.md
- 版本：v0.1
- 是否封版：N（等 WORKLOG + SYNC_STATUS 完成後封版）
- 已知問題：
  - GitHub Repo 尚未建立（需 Ray 動作）
  - SYNC_STATUS.md 尚未建立（下次開機 P0）
  - Codex 仍停線（TASK-002 HOLD）
```
