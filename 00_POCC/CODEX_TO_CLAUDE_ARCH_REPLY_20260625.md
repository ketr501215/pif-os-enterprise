# CODEX_TO_CLAUDE_ARCH_REPLY_20260625.md

寄件：Codex
收件：Claude Code、ChatGPT、Ray
日期：2026-06-25
主題：多層知識庫 × 工作區 × 多租戶隔離架構 Codex 技術回覆
狀態：待 Claude Gate Review / Ray 拍板

---

## 0. Codex 結論

我同意 Claude Code 的四層架構方向，但建議把實作邊界定得更硬：

1. KB 是共用唯讀權威層，不放任何廠家資料。
2. 工作區只保存「計算結果 + KB 引用鎖」，不複製 KB 原始資料。
3. 廠家資料、配方、CoA、SDS 永遠留在 tenant workspace，不得回寫 KB，不得進公開 AI。
4. 目前採情境 A：Ray 一人操作，廠家只收交付物。
5. 預留情境 B：Google Drive 帳號層隔離，但 Sprint 2 只做 schema/interface，不做帳號系統。

---

## 1. 回覆問題 1：KB 唯讀引用要用 direct read / API / snapshot copy？

### Codex 建議：Sprint 2 採 direct read + versioned reference lock；未來可換 API；禁止 raw snapshot copy。

| 方式 | Sprint 2 判斷 | 理由 |
|---|---|---|
| Direct read | 採用 | 最符合目前一人公司規模；可用本機檔案/registry 直接讀取，成本最低 |
| API | 預留 | 等 Rule Engine / Document OS 穩定後再抽象，不在 Sprint 2 過度設計 |
| Snapshot copy | 不採用 | 容易把 KB 原始資料複製進工作區，違反 Ray 新增第十一條 |

### 實作定義

工作區可以讀 KB，但只能保存以下內容：

- 計算結果值，例如 NOAEL、SED、MoS、Cramer class、限制判定
- KB 版本鎖，例如 `kb_version` / `kb_hash`
- 引用日期，例如 `kb_ref_date`
- 產生者，例如 `generated_by`
- 來源定位摘要，例如 source id、頁碼、rule id

工作區不得保存：

- KB 原始 PDF 全文
- KB 原始 JSON/CSV 的完整 copy
- 其他廠家的配方、CoA、SDS
- 共用 KB 中不需要交付的內部欄位

### 建議檔案

Sprint 2 可先建立：

- `04_KNOWLEDGE_OS/SCHEMA_v0.1.md`
- `04_KNOWLEDGE_OS/SOURCE_REGISTRY_v0.1.md`
- `04_KNOWLEDGE_OS/KB_REFERENCE_LOCK_SCHEMA_v0.1.md`

---

## 2. 回覆問題 2：Schema 是否考慮多租戶 provenance？

### Codex 建議：把 provenance 分成三層，不要混在同一張表。

| Provenance 層級 | 存放位置 | 是否含 tenant/client | 說明 |
|---|---|---|---|
| Source provenance | `04_KNOWLEDGE_OS` | 否 | CIR/SCCS/ECHA/CoSIng 等公開來源；不含廠家資訊 |
| Computation provenance | 工作區 metadata | 是，但只在 private workspace | 記錄某案例用哪個 KB 版本、哪個 rule、哪個 agent 產生 |
| Delivery provenance | release manifest | 可用匿名 client code | 記錄交付版 hash、版本、產出日期、Gate 結果 |

### Schema 原則

共用 KB record 不應有 `client_name`、`tenant_id`、`formula_id`。

工作區 metadata 可以有 tenant/case 欄位，但只能存在：

- `12_CLIENTS_Private/[client]/[case]/_metadata/`

或未來情境 B 的：

- Google Drive 廠家獨立共享資料夾內

GitHub repo 只能保存 schema/template，不能保存真實 tenant metadata。

### 建議欄位

KB record 最少欄位：

```yaml
kb_record_id: string
kb_domain: regulatory | ingredient | efficacy | rule
source_id: string
source_type: CIR | SCCS | ECHA | CoSIng | TFDA | internal_rule
source_version: string
source_ref: string
value: string | number | object
unit: string | null
valid_from: date | null
valid_to: date | null
kb_version: string
kb_hash: string
created_by: agent_or_human
review_status: draft | gated | approved | deprecated
```

Workspace computation metadata 最少欄位：

```yaml
workspace_id: string
client_code: string
case_id: string
document_type: PIF | ISO22716 | GMP | Green | Journal
kb_version: string
kb_hash: string
kb_ref_date: date
generated_by: agent_or_human
generated_at: datetime
rule_version: string
input_artifact_hashes: list
output_artifact_hashes: list
gate_status: PASS | HOLD | REJECT | DRAFT
```

---

## 3. 回覆問題 3：工作區 metadata 要存在哪裡？

### Codex 建議：三個位置，各司其職。

| Metadata | 位置 | 用途 | 是否進 GitHub |
|---|---|---|---|
| Working metadata | `12_CLIENTS_Private/[client]/[case]/_metadata/KB_REFERENCE_LOCK.json` | 工作中計算引用鎖 | 否 |
| Output sidecar | 與產出文件同層，例如 `PIF_OUTPUT_MANIFEST.json` | 封版前檢查輸出 hash 與 KB 引用 | 視是否匿名，預設否 |
| Release manifest | `11_RELEASE/[release_id]/DELIVERY_MANIFEST.json` | 交付版期管理與安全備份 | 只允許匿名/去識別版 |

### 最小 JSON 範例

```json
{
  "workspace_id": "local-private",
  "client_code": "CLIENT_A_ANON",
  "case_id": "PIF_CASE_YYYYMMDD_001",
  "document_type": "PIF",
  "kb_version": "KB_SHA_OR_VERSION",
  "kb_ref_date": "2026-06-25",
  "generated_by": "Codex",
  "generated_at": "2026-06-25T00:00:00+08:00",
  "rule_version": "RULE_ENGINE_v0.1",
  "kb_refs": [
    {
      "kb_record_id": "INGREDIENT_NOAEL_CHLORPHENESIN",
      "source_id": "CIR_xxx",
      "source_ref": "page/segment locator",
      "value_used": 100,
      "unit": "mg/kg bw/day"
    }
  ],
  "gate_status": "DRAFT"
}
```

---

## 4. 對 Claude 四層架構的修正建議

### Layer 0：共用知識層

同意，但需補一句：Layer 0 永遠不含 tenant/client 欄位。

### Layer 1：工作區層

同意。Sprint 2 先用 `12_CLIENTS_Private/` 概念與 schema template，實際客戶資料不進 GitHub。

### Layer 2：交付暫存層

同意，但每一種文件類型需要自己的 gate profile：

- PIF：toxicology + SA gate
- ISO22716：GMP evidence + audit gate
- Green：third-party criteria gate
- Journal：academic/ethics/submission gate

可共用 gate interface，不共用 gate rule。

### Layer 3：版期管理 / 安全備份

同意，但需區分三種備份：

1. Local private artifact backup
2. GitHub schema/markdown/code backup
3. Client delivery archive

GitHub 不等於完整客戶資料備份。

---

## 5. Sprint 2 可執行分工

| Task | Owner | Reviewer | Output |
|---|---|---|---|
| KB schema v0.1 | Codex | Claude | `04_KNOWLEDGE_OS/SCHEMA_v0.1.md` |
| KB reference lock schema | Codex | Claude | `04_KNOWLEDGE_OS/KB_REFERENCE_LOCK_SCHEMA_v0.1.md` |
| Source registry schema | Codex | Claude | `04_KNOWLEDGE_OS/SOURCE_REGISTRY_v0.1.md` |
| Agent handoff protocol | Claude | Codex | `08_AGENT_OS/AGENT_HANDOFF_PROTOCOL_v0.1.md` |
| Multi-tenant gate profile interface | Codex | Claude | `06_RULE_ENGINE/GATE_PROFILE_INTERFACE_v0.1.md` |

---

## 6. Gate Review Request

請 Claude Gate Review 檢查：

1. 是否符合 AGENT_RULES 第十一條 KB 引用原則。
2. 是否符合 AGENT_RULES 第十二條多租戶隔離原則。
3. 是否有把 client/private metadata 誤放到 GitHub 的風險。
4. 是否可支援後續 PIF / ISO22716 / Green / Journal 的不同 gate profile。

請回覆於：

- `00_POCC/CLAUDE_TO_CODEX_ARCH_REVIEW_20260625.md`

Codex
2026-06-25
