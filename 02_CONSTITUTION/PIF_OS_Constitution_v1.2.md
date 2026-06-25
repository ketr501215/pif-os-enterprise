# PIF OS Enterprise — Constitution v1.2
# 制定：Ray（Product Owner）
# 執行：Claude Code
# 日期：2026-06-25
# 版本：v1.2（v1.1 納入 ADR-010；v1.2 納入 Project Priority Governance）

---

## 前言

本 Constitution 是 PIF OS Enterprise 的最高治理文件。
所有 Agent、所有 Work Package、所有交付物，均受本文件約束。
修改本文件需 Ray 明確拍板，且必須記錄於 DECISION_LOG.md。

---

## Article 1｜系統定位

PIF OS Enterprise 是一人公司 AI Operating System。
PIF + ISO22716 是第一個產品線（reference implementation），不是整個系統。
其餘產品線（GMP / 綠色無毒 / 期刊投稿 / 其他文件服務）比照 Plugin 掛載。

---

## Article 2｜知識層架構（四層）

```
Layer 0：共用知識層（雲端，永久唯讀）
  法規KB / 原料KB / 功效KB
  ⚠️ 不含任何 tenant/client 欄位

Layer 1：工作區層（廠家隔離）
  12_CLIENTS_Private/[client]/[case]/
  ⚠️ 廠家之間完全隔離，不得互視

Layer 2：交付暫存層（Gate + SA 簽核）
  每種文件類型有獨立 Gate Rule，共用 Gate Interface

Layer 3：版期管理 / 安全備份（三種備份，性質不同）
  - 本機私有備份（F:，含客戶資料）
  - GitHub 備份（schema/markdown/code，無客戶資料）
  - 客戶交付 Archive（封版後，SA 簽核）
```

---

## Article 3｜KB 引用原則（ADR-010，Ray 核可 2026-06-25）

**工作區不複製 KB 原始資料，只引用計算結果。**

1. KB 採 `direct read + versioned reference lock`，禁止 snapshot copy
2. 工作區只保存：計算結果值 + KB 引用鎖（kb_version / kb_hash / kb_ref_date / generated_by）
3. KB 更新不自動影響已封版交付物，更新需人工重產
4. 廠家資料、配方、CoA、SDS 不得回寫 KB
5. 共用 KB record 不含 client_name / tenant_id / formula_id

**Metadata 必填欄位：**
`kb_version`、`kb_hash`、`kb_ref_date`、`generated_by`、`source_ref`

---

## Article 4｜多租戶隔離原則（ADR-010，Ray 核可 2026-06-25）

**現行情境 A，預留情境 B 介面。**

### 情境 A（現行）
- Ray 一人操作，廠家只收交付物
- 廠家資料存於 `12_CLIENTS_Private/[client]/[case]/`
- 各廠家資料夾完全隔離

### 情境 B（預留，Sprint 2 只做 Schema Interface）
- 廠家取得獨立 Google Drive 共享資料夾
- Google 帳號層技術隔離
- KB 唯讀共享，廠家無法修改

### 跨情境鐵則（任何情境皆不可違反）
- 廠家 A 資料不得出現在廠家 B 視野
- 配方/CoA/SDS 只在本機 F: 或廠家獨立隔離空間
- 公開 AI 只能接觸公開 KB，不得接觸廠家私密資料
- GitHub repo 只放 schema/template/code/POCC 文件，不放真實客戶資料

---

## Article 5｜Gate 原則

1. 每種文件類型有獨立 Gate Rule（PIF / ISO22716 / GMP / 綠色 / 期刊）
2. 共用 Gate Interface（`06_RULE_ENGINE/GATE_PROFILE_INTERFACE_v0.1.md`）
3. 雙重檢核：主責 Agent 完成後，檢核 Agent 只讀最終輸出
4. Gate PASS 才能進入交付暫存層
5. SA 簽核 + Ray 拍板才能 promote 至正式交付

---

## Article 6｜Agent 分工最高原則

| 原則 | 說明 |
|------|------|
| 無聊天記憶 | 所有決定必須落地為檔案 |
| SSOT | 每次開機先讀 EXECUTIVE_DASHBOARD.md |
| Mailbox 雙向 | 各 Agent 每日必讀對方 mailbox |
| 交接卡強制 | 每個 WP 完成必須產出交接卡 |
| 任何 AI 都不能是唯一決策者 | 核心裁決必須 Ray 確認或 SA 簽核 |

---



---

## Article 8｜Project Priority Governance（ChatGPT 提案，Ray 核可 2026-06-25）

### 子系統優先序

| 序 | 子系統 | 優先級 | 主責 Agent |
|----|--------|--------|-----------|
| 1 | 法規知識庫、原料知識庫、功效知識庫 | 🔴 P0 | Codex（Gate: Claude Code）|
| 2 | 文件管理系統（PIF / ISO 22716 / GMP / 綠色 / 期刊）| 🟡 P1 | Claude Code（PMO: ChatGPT）|
| 3 | 版期管理與安全備份 | 🟢 P2 | Claude Code + Gemini CLI |

### 每日 Agent 工作日報（Daily Agent Report）

**格式（ChatGPT 補強版，2026-06-25 生效）：**

```markdown
# DAILY_[Agent]_YYYYMMDD

- Agent:
- 日期:
- 昨日達成:         ← 必填，無則明確寫「無」
- 今日計畫:         ← 必填
- Blockers:         ← 阻塞原因 + 需誰解決
- Need Review:      ← 需其他 Agent Gate Review 的事項
- Need Ray Decision:← 需 Ray 拍板的事項（不得 Agent 間自行裁決）
- Next Agent:       ← 完成後下一棒交給誰、交什麼
```

### Gate Review 制度
- 主責：Claude Code
- 原則：只讀最終輸出，不讀中間過程
- 結論三態：PASS / CONDITIONAL PASS / HOLD

### PMO Dashboard
- 主責：ChatGPT
- 週期：每次重大 WP 封版後更新
- 內容：Sprint 進度、風險、決策待辦

---

## Article 9｜修改程序

1. 任何 Agent 提出修改 → 寫 ADR_XXX_PROPOSAL 文件
2. Ray 審閱 → 拍板（採納 / 拒絕 / 修改後採納）
3. Claude Code 更新本文件 + 版本號遞增
4. 所有 Agent 下次開工前重讀

---

> 本文件版本：v1.2
> 生效日：2026-06-25
> 制定：Ray | 維護：Claude Code
> 修訂歷程：v1.0 Gemini 草稿 → v1.1 ADR-010（KB隔離+多租戶）→ v1.2 Project Priority Governance（ChatGPT提案）
