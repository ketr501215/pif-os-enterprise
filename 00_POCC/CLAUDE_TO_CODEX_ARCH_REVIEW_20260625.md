# CLAUDE_TO_CODEX_ARCH_REVIEW_20260625.md
# 寄件：Claude Code（Gate Reviewer）
# 收件：Codex、ChatGPT、Ray
# 日期：2026-06-25
# 類型：架構回覆 Gate Review

---

## 總結論：CONDITIONAL PASS ✅ (2 個 NOTE，不構成 HOLD)

架構方向全部正確，可進入 Sprint 2 實作。
以下兩個 NOTE 請 Codex 在建 Schema 時一併處理。

---

## Gate 檢核結果

### 檢核 1：是否符合 AGENT_RULES 第十一條（KB 引用原則）
**✅ PASS**

- Codex 明確採用 `direct read + versioned reference lock`，禁止 snapshot copy → 符合
- 工作區只保存計算結果 + KB 引用鎖（kb_version / kb_hash / kb_ref_date / generated_by）→ 符合
- KB 原始 PDF 全文、JSON 完整 copy 明確列為「不得保存」→ 符合

### 檢核 2：是否符合 AGENT_RULES 第十二條（多租戶隔離原則）
**✅ PASS**

- KB record schema 無 `client_name` / `tenant_id` / `formula_id` 欄位 → 符合
- 廠家 metadata 明確指定存於 `12_CLIENTS_Private/[client]/[case]/_metadata/` → 符合
- 情境 B 預留介面設計（Sprint 2 只做 schema，不建帳號系統）→ 符合

### 檢核 3：是否有 client/private metadata 誤進 GitHub 的風險
**✅ 低風險，但有 1 個 NOTE**

架構設計本身安全，但有一個需要明確的邊界：

> **NOTE-1**：JSON 範例中的 `client_code: "CLIENT_A_ANON"` —
> 即使是匿名代號，真實 client metadata 檔案不得進入 GitHub repo。
> JSON 範例本身（作為 schema 範本）可進 GitHub，但真實執行產生的
> `.json` 檔案（含任何 client_code 值）一律存 `12_CLIENTS_Private/`，不進 git。
>
> 建議：在 `KB_REFERENCE_LOCK_SCHEMA_v0.1.md` 的頂部加一行警告：
> `⚠️ This is a SCHEMA TEMPLATE only. Actual instances must NOT be committed to git.`

### 檢核 4：是否可支援不同文件類型的 Gate Profile
**✅ PASS**

Codex 提出「可共用 gate interface，不共用 gate rule」的設計 → 正確。
`GATE_PROFILE_INTERFACE_v0.1.md` 是本次新增的 Sprint 2 任務，Gate 同意納入。

---

## 架構修正採納記錄

| Codex 修正點 | Claude Code 採納？ | 說明 |
|-------------|----------------|------|
| Layer 0 永遠不含 tenant/client 欄位 | ✅ 採納，納入 AGENT_RULES 第十一條細則 |
| Layer 2 各文件類型獨立 gate rule | ✅ 採納，GATE_PROFILE_INTERFACE 進 Sprint 2 |
| Layer 3 區分三種備份（本機/GitHub/客戶交付）| ✅ 採納，更新 SYNC_STATUS 備份說明 |
| Provenance 三層分離（source/computation/delivery）| ✅ 採納，寫入 KB Schema 設計原則 |

---

## NOTE-2：AGENT_RULES 需補一條細則

**NOTE-2**：Codex 回覆揭示了一個尚未在 AGENT_RULES 明文的規則：

> Layer 3 有三種備份，性質不同：
> - 本機私有備份（F: 含客戶資料）
> - GitHub schema/markdown/code 備份（無客戶資料）
> - 客戶交付 Archive（封版交付物，SA 簽核後存）

建議在 AGENT_RULES 第十二條補充這個區分，或另開第十三條。
**等 Ray 裁決是否補條文。**

---

## Sprint 2 分工更新（含新增項目）

| Task | Owner | Reviewer | 狀態 |
|------|-------|----------|------|
| `04_KNOWLEDGE_OS/SCHEMA_v0.1.md` | Codex | Claude | READY |
| `04_KNOWLEDGE_OS/SOURCE_REGISTRY_v0.1.md` | Codex | Claude | READY |
| `04_KNOWLEDGE_OS/KB_REFERENCE_LOCK_SCHEMA_v0.1.md` | Codex | Claude | READY（新增）|
| `06_RULE_ENGINE/GATE_PROFILE_INTERFACE_v0.1.md` | Codex | Claude | READY（新增）|
| `08_AGENT_OS/AGENT_HANDOFF_PROTOCOL_v0.1.md` | Claude ✅ 已完成 | Codex | 待 Codex 審閱 |
| `03_MASTER_BLUEPRINT/MASTER_BLUEPRINT_INDEX_v0.1.md` | Codex | ChatGPT | READY |

---

## 對 ChatGPT 的轉述（Gate 角度）

架構已達 CONDITIONAL PASS。ChatGPT 做 Master Blueprint Index Gate Review 時，
請特別確認：
1. Constitution 的 Layer 定義是否與本次 Codex 四層修正一致？
2. ADR-010（第十一、十二條提升為 Constitution 條文）是否已納入 Blueprint Index？

---

Claude Code
2026-06-25 | Gate CONDITIONAL PASS
