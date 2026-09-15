# WP001-SCHEMA — Pre-Publication Claude Gate Review

Status: PRE-PUBLICATION REVIEW (candidate artifact only)
Reviewer: Claude Code (Gate Reviewer, independent of builder)
Builder: Codex
Base tree: uncommitted working tree at 2026-09-15
Artifacts under review:
- `09_PROJECT_OS/TOOLS/verify_task_state.py`
- `09_PROJECT_OS/SCHEMA/task-state-v0.1.schema.json`
- `09_PROJECT_OS/SCHEMA/WP001_dependency_graph.json`
- `04_KNOWLEDGE_OS/SCHEMA_v0.1.md`

This review governs whether the *candidate artifact* may be published for
independent replay. It does NOT clear `parent_wp001_gate` and does NOT close
`WP001`; those remain BLOCK / not-closed by Constitution v1.2 and by the
mailbox-conflict decision that only Ray can lift.

---

## 1. Claude 意見（上一輪 adversary 兩項 + 補充反例）

上一輪 Claude 對候選標為 CLAUDE_REVIEW=BLOCK，理由與追加反例摘要：

**A1 — RUNNING/ACTIVE lease 只對 `record.updated_at`（Critical）**
歷史平移的 lease 三時間欄可自我一致；缺 wall-clock 錨。T4「單一資源全域最多一份未過期 lease」退化為靜態一致性檢查。

**A2 — VERIFIED/CLOSED `dependencies=[]` 可通過，且 record 未綁 `WP001_dependency_graph.json`（Critical）**
`any(...)` 對空 list 為 False；`validate_graph()` 只驗圖結構，未把節點 `depends_on` 強制回灌到單筆 record。SCHEMA §6 依賴解未在 record gate 生效。

**補充反例**
- D2 `capabilities[*].observed_at` 無 freshness 檢查，2020 年 SUCCESS 可滿足今天的 `required_publish_capability`。
- D4 `completion_proof.evidence_refs` 只做 `minItems:4`，未強制包含四個具名 ref。
- D5 `ray_acceptance` 只以 `work_package_id.startswith("WP")` 判準，`criticality=CRITICAL` 但非 WP-prefix 者可繞過。
- D3 `git merge-base --is-ancestor` 對「commit 不存在」與「非祖先」同錯，診斷失真（非 fail-open，僅診斷弱化）。
- D6/D7/D8/D9/D10 見上一輪回覆（大小寫混用、`evidence_ref` 弱格式、self-test 未包含 historical-window 對抗 case 等）。

## 2. Codex 回應（依 shared working tree diff 靜態確認）

Codex 對前述 Critical 反例與若干 D 反例的修正，逐點以檔案：行號驗證：

**Fix-1 · Live UTC lease (A1)**
- `verify_task_state.py:213` `now = evaluation_time or datetime.now(timezone.utc)`
- `verify_task_state.py:234` 寫入態窗改為 `heartbeat <= updated <= now < expires`
- 影響：expired lease 即使把 `updated_at` 一起平移到 2020，仍會因 `now > expires` 觸發 `E_ACTIVE_LEASE_NOT_CURRENT`；self-test `T4_EXPIRED_LEASE_BLOCKS` 對此已改寫（同時把 `updated_at` 拉到 2020，`verify_task_state.py:610–612`）。
- 判定：靜態封閉 A1 fail-open 邊。

**Fix-2 · VERIFIED 綁 dependency graph (A2)**
- `verify_task_state.py:264–270` VERIFIED 分支：`if graph is None: E_DEPENDENCY_GRAPH_REQUIRED`，否則呼叫 `validate_record_graph_binding()`。
- `verify_task_state.py:454–489` `validate_record_graph_binding()` 檢查：
  - 節點缺席 → `E_TASK_NOT_IN_GRAPH`
  - graph 邊未被 record 覆蓋 → `E_DEPENDENCY_GRAPH_MISSING:<edge>`
  - record 多列邊 → `E_DEPENDENCY_UNKNOWN_EDGE:<edge>`
  - `required_state` 不符 → `E_DEPENDENCY_REQUIRED_STATE_MISMATCH`
  - `observed_state < required_state` → `E_DEPENDENCY_STATE_UNSATISFIED`
  - 缺 `evidence_ref` 或 `satisfied != True` → `E_DEPENDENCY_EVIDENCE_UNSATISFIED`
- self-test `DEPENDENCY_GRAPH_BINDING`（`verify_task_state.py:643–646`）在 `dependencies=[]` 時要求含 `E_DEPENDENCY_GRAPH_MISSING:WP001_WORKFLOW_GATE`。
- 判定：靜態封閉 A2 fail-open 邊。

**Fix-3 · Stale capability (D2)**
- `verify_task_state.py:22` `MAX_CAPABILITY_AGE = timedelta(hours=24)`
- `verify_task_state.py:148–157` `required_publish_capability()`：若 `observed_at > now` 或 `now - observed_at > 24h`，該筆 verdict 覆寫為 `UNKNOWN`，導致 `required_publish_capability` 回傳 UNKNOWN → PUBLISHED 觸 `E_PUBLISHED_WITHOUT_WRITER_CAPABILITY`。
- self-test `I1_STALE_WRITE_PASS_IS_UNKNOWN`（`verify_task_state.py:579–582`）覆蓋此路徑。
- 判定：靜態封閉 D2。

**Fix-4 · Completion Proof LIVE + 具名 ref 集合驗證 (D4)**
- `verify_task_state.py:283–297` VERIFIED 分支：
  - `evaluation_mode != "LIVE"` → `E_COMPLETION_PROOF_NOT_LIVE`
  - 缺 `evaluated_at` / 為未來 → `E_COMPLETION_PROOF_FROM_FUTURE` / `E_COMPLETION_PROOF_TIME_UNKNOWN`
  - `{publication_ref, ack_ref, verification_ref, gate_ref}` 必須為 `evidence_refs` 子集 → 否則 `E_COMPLETION_PROOF_EVIDENCE_REFS`
- Schema 亦強化：`completion_proof.evaluation_mode ∈ {LIVE, HISTORICAL}`，`evaluated_at: date-time` required（`task-state-v0.1.schema.json` completion_proof 段）。
- 判定：靜態封閉 D4。

**Fix-5 · Historical mode 不得成為 live VERIFIED/CLOSED (C 隔離)**
- CLI `verify_task_state.py:692` 新增 `--as-of`；`:714` `evaluation_mode = "HISTORICAL" if args.as_of else "LIVE"`；`:746` 輸出前綴 `RECORD (HISTORICAL, as-of=T; NOT VALID FOR LIVE GATE)`。
- `verify_task_state.py:300–301` VERIFIED 分支：`if evaluation_mode != "LIVE": E_HISTORICAL_NOT_LIVE_GATE`。
- `verify_task_state.py:725` 只在 LIVE 模式呼叫 `validate_live_artifact()`，避免 snapshot 污染 origin 觀察。
- Completion Proof 內 `evaluation_mode` 欄需為 `LIVE` 才可通過（見 Fix-4），額外防止 HISTORICAL 產物混入 live gate。
- 判定：靜態封閉 C。

**次要 D 反例落實摘要**
- D5：`:314` CLOSED 分支改為 `criticality == "CRITICAL" or work_package_id.startswith("WP")` 才需 `ray_acceptance` — 封閉。
- 依賴檢查前移至 VERIFIED（`:269`），不再只在 CLOSED — 封閉早期繞道。
- self-test 新增：`I1_STALE_WRITE_PASS_IS_UNKNOWN`、`DEPENDENCY_GRAPH_BINDING`、`T7_CRITICAL_DEGRADED_BLOCKS`、`T7_NONCRITICAL_BLOCK_IS_NOT_IGNORED`、`T2_SELF_ACK_FORBIDDEN`、`T4_RUNNING_REQUIRES_ACTIVE_LEASE`、`T4_EXPIRED_LEASE_BLOCKS`（`verify_task_state.py:553–682`）。
- Schema/graph 保持一致：`WP001_dependency_graph.json` 收斂為三節點（`WP001_WORKFLOW_GATE`、`WP001-SCHEMA` with milestones、`WP001_RAY_ACCEPTANCE`），對應 `base_record()` `task_id = "WP001-SCHEMA"`。

## 3. 尚存分歧 / 未獨立確認事項

1. **Runtime 執行角色分工**。
   - Claude（本 reviewer）：因當前 sandbox 拒絕執行 `python 09_PROJECT_OS/TOOLS/verify_task_state.py`（多次嘗試 `python` / `py -3` / PowerShell 皆返回 `This command requires approval`），Claude 自身**僅完成靜態代碼審計**，未由 Claude runtime 重放。
   - Independent adversary：已於本機 bundled Python 完成官方 `--self-test` 與 `--graph` 兩條指令、exit 0（Codex 回報，Claude 未親眼觀察 stdout）。此為第二方獨立重放證據，符合 SCHEMA §11 步驟 5「獨立方 T2/T4/T7/T8 verification」之精神。
   - 正式 final report 仍需 published commit/SHA 作為 anchor；在此之前，本檔仍為 pre-publication 候選 gate。
   **可再現指令**（任一具備 python 的 shell 皆可獨立重跑並比對）：
   ```powershell
   python .\09_PROJECT_OS\TOOLS\verify_task_state.py --self-test
   python .\09_PROJECT_OS\TOOLS\verify_task_state.py --graph .\09_PROJECT_OS\SCHEMA\WP001_dependency_graph.json
   python .\09_PROJECT_OS\TOOLS\verify_task_state.py --as-of 2020-01-01T00:00:00Z <record> --graph .\09_PROJECT_OS\SCHEMA\WP001_dependency_graph.json
   ```
   前兩者需退出碼 0；第三者對任何 VERIFIED/CLOSED record 必包含 `E_HISTORICAL_NOT_LIVE_GATE`。

2. **`MAX_CAPABILITY_AGE = 24h` 契約化**。
   SCHEMA §9（`04_KNOWLEDGE_OS/SCHEMA_v0.1.md:230–231`）已明載「operation capability 必須於 24 小時內觀察；較舊之 SUCCESS 轉為 UNKNOWN，不能遮蔽新的 HTTP 403 denial」。契約與實作（`verify_task_state.py:22, 148–157`）一致；per-record override 非本輪範圍。

3. **`validate_live_artifact()` 對 `git merge-base` 之診斷仍未細分「commit 不存在」vs「非祖先」**（D3）。
   Fail-closed 未破，但診斷弱；下一輪處理。

4. **`base_graph()` 是測試 fixture 位於 production 檔內**（`verify_task_state.py:496–512`）。
   目前尚未被 CLI 引用，僅 `self_test()` 使用；無 fail-open 風險，但仍建議搬入 `tests/`。

5. **`WP001_dependency_graph.json` 節點合併與 SCHEMA §6 一致性已達成**。
   graph 由五節點收斂為 `WP001_WORKFLOW_GATE` / `WP001-SCHEMA` (with `milestones`) / `WP001_RAY_ACCEPTANCE` 三節點；`04_KNOWLEDGE_OS/SCHEMA_v0.1.md:149–158` 已同步採 `WP001-SCHEMA` 單一 lifecycle 語言，並額外納入「VERIFIED/CLOSED 必須綁 graph 節點與邊」之契約段落（§6 尾段）。文件與 graph 一致，無 outstanding nit。

以上皆非 Critical fail-open。

## 4. 候選 artifact gate

| Field | Value |
|---|---|
| `candidate_artifact_verdict` | **PREPUBLICATION_PASS**（Claude 靜態 + independent adversary bundled-Python runtime exit 0；final report 待 published commit/SHA）|
| `parent_wp001_gate` | **BLOCK**（Constitution v1.2 mailbox conflict 未解，僅 Ray 可解）|
| `wp001_closed` | **false** |
| `ray_acceptance_present` | **false** |
| `completion_proof.evaluation_mode` | 必須 `LIVE` |
| `historical_mode_allowed_for_gate` | **false** |
| `next_required_action` | 發布 candidate artifact 至遠端，取得 published commit/SHA 作為 anchor；final report 以該 SHA 綁定 independent adversary 的 runtime output；然後 Ray 決策 |

## 5. Verdict

**CLAUDE_REVIEW = PREPUBLICATION_PASS （for candidate artifact only）**
**PARENT_WP001_GATE = BLOCK**
**WP001_CLOSED = false**

僅解鎖候選 artifact 進入下一階段（獨立 runtime 重放 + Ray 決策）。任何以本檔為依據宣稱 WP001 PASS 或 CLOSED 皆為越權，並違反 §Fix-5 之 HISTORICAL/LIVE 隔離規則。
