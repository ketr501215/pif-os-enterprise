# AGENT_HANDOFF_PROTOCOL_v0.1.md
# PIF OS Enterprise — Agent 交接協議
# 主責：Claude Code | 版本：v0.1 | 日期：2026-06-25
# 審閱：Codex

---

## 一、核心原則

1. **無聊天記憶**：所有決定必須落地為檔案，不得存在 chat history 中
2. **SSOT 優先**：每次開機先讀 `00_POCC/EXECUTIVE_DASHBOARD.md` + `SPRINT2_COORDINATION_BOARD_*.md`
3. **Mailbox 雙向**：Claude 讀 `CODEX_TO_CLAUDE_*`，Codex 讀 `CLAUDE_TO_CODEX_*`，不得跳過
4. **交接卡強制**：每個 Work Package 完成必須產出交接卡，否則不算封版

---

## 二、Mailbox 命名規則

```
寄件人_TO_收件人_主題_日期.md

範例：
  CLAUDE_TO_CODEX_SPRINT2_COORDINATION_20260625.md
  CODEX_TO_CLAUDE_SPRINT2_REPLY_20260625.md
  CLAUDE_TO_CODEX_SPRINT2_REVIEW_20260625.md   ← ACK 回覆
```

### 主題命名速查
| 類型 | 主題關鍵字 |
|------|-----------|
| 協商 | `COORDINATION` |
| 回覆 | `REPLY` |
| 確認/ACK | `REVIEW` or `ACK` |
| 緊急校正 | `CORRECTION` |
| 移交 | `HANDOFF` |

---

## 三、每日開機 SOP（固化版）

```
Step 1  git pull（確認本機是最新）
Step 2  讀 00_POCC/EXECUTIVE_DASHBOARD.md
Step 3  讀 00_POCC/SPRINT2_COORDINATION_BOARD_*.md（若存在）
Step 4  讀對方 mailbox（CODEX_TO_CLAUDE_* 或 CLAUDE_TO_CODEX_*）
Step 5  確認 SYNC_STATUS.md（F: = GitHub 是否一致）
Step 6  開始執行最高優先任務
```

**⚠️ Step 4 不得跳過**，即使沒有新信也要確認無新檔案。

---

## 四、交接卡格式（強制）

每個 Work Package 封版時必須產出：

```markdown
## 交接卡 [WP-XXX] v[版本]

- 日期：YYYY-MM-DD
- 主責：[Claude Code / Codex / Ray]
- 輸入：[依賴哪些檔案/決策]
- 完成清單：
  - ✅ [具體交付物，含路徑]
- 輸出：[本 WP 產出的主要檔案]
- 待下一位：
  - [Agent名稱] → [具體動作]
- 已知問題：[或寫「無」]
- 封版：[Y/N]，git hash: [hash]
```

---

## 五、雙重檢核規則

| 主責 | 檢核人 | 觸發條件 | 限制 |
|------|--------|----------|------|
| Codex（Schema/Knowledge 填充） | Claude Code | 每次 staging 更新 | 檢核人只讀最終輸出，不讀中間過程 |
| Claude Code（POCC 文件/Protocol） | Codex | 每次 WP 封版 | 同上 |
| 任何人（production promote） | Ray | promote 前 | SA 簽核視情況加入 |

**同圈驗證禁止**：若 A 的輸出直接影響 A 自身的驗證判斷，必須引入第三方（Ray 或 SA）。

---

## 六、緊急校正協議

發現錯誤時：
1. 立刻寫 `SENDER_TO_RECEIVER_CORRECTION_日期.md`，說明錯誤內容 + 影響範圍
2. 在 TASK_BOARD.md 標記相關任務為 `HOLD`
3. 不得在對方 mailbox 回覆前逕自修改 production 檔案
4. BUG 修正需：重抽 → Gate PASS → SA 簽 → Ray 拍板 → promote

---

## 七、禁止行為（硬規則）

- ❌ 覆蓋對方已封版的檔案（需先取得 ACK）
- ❌ 把客戶資料（配方/CoA/SDS）寫入 git repo
- ❌ 單一 Agent 自行 promote production（必須雙方 Gate + Ray）
- ❌ 在 chat 中做決策不落地為檔案
- ❌ 跳過 mailbox 直接開工

---

## 審閱請求

Codex 請確認：
- [ ] 命名規則是否與你的 session 習慣一致？
- [ ] Step 4 mailbox 確認流程是否可執行？
- [ ] 雙重檢核規則是否符合你在 SPRINT2_REPLY 中的描述？

版本：v0.1（待 Codex 審閱後升 v1.0）
