# Decision Log

## D001 - Enterprise Scope

Date: 2026-06-25
Decision: PIF OS Enterprise is a one-person-company AI operating system. PIF + ISO22716 is the first product line/reference implementation.
Reason: Avoid reducing the project to only PIF delivery while still using PIF/ISO as the immediate revenue engine.

## D002 - POCC Folder Name

Date: 2026-06-25
Decision: The folder name is fixed as `00_POCC`.
Reason: POCC is a function, not an agent ownership label. Agent names are allowed only in mailbox file names.

## D003 - Git Backup Scope

Date: 2026-06-25
Decision: Initialize safe local Git baseline first; GitHub private remote remains pending until authorized remote is available.
Reason: Prevent false backup claims and avoid leaking confidential client data.

## D004 - First Architecture to Establish

Date: 2026-06-25
Decision: First architecture is the POCC v0.2 + Business OS Sprint 1 + PIF/ISO product-line skeleton.
Reason: This creates a restartable company control center before deeper engine/database work begins.

## D005 - KB 與工作區引用原則

Date: 2026-06-25
Decision: 工作區不複製 KB 原始資料，只引用計算結果。Metadata 必須記錄 KB 版本號與引用日期。KB 更新不自動影響已封版 PIF，需人工重產。
Reason: 防止 KB 污染；確保每份 PIF 可追溯到產製當時的知識狀態。
Owner: Ray 拍板 | 寫入 AGENT_RULES.md 第十一條

## D006 - 多租戶隔離策略

Date: 2026-06-25
Decision: 現行採情境 A（廠家只收交付物，Ray 一人操作），預留情境 B 介面（廠家有 Google Drive 帳號，帳號層隔離）。
Reason: 情境 A 成本最低，符合當前一人公司規模；情境 B 是未來「導入」的自然擴充路徑，預留不做過度設計。
Owner: Ray 拍板 | 寫入 AGENT_RULES.md 第十二條

## ADR-010 - KB 引用與多租戶隔離提升為 Constitution 條文

Date: 2026-06-25
Decision: AGENT_RULES 第十一條（KB 引用原則）與第十二條（多租戶隔離）正式提升為 Constitution Article 3 & Article 4。Constitution 版本從 v1.0（Gemini 草稿）升為 v1.1。
Reason: 這兩條是整個系統的核心治理原則，需更高修改門檻；ChatGPT 提案，Claude Code 支持，Ray 採納。
Owner: Ray 拍板 | 執行：Claude Code | 文件：02_CONSTITUTION/PIF_OS_Constitution_v1.1.md

## D007 - WP-006A 部份採納

Date: 2026-06-25
Decision: ChatGPT WP-006A 三項提案中：提案 1（00_EXECUTIVE）拒絕（與 00_POCC 重複）；提案 2（01→10_BUSINESS_OS 改號）拒絕（與 10_PRODUCT_LINES 撞號）；提案 3（08_AGENT_OS 子資料夾）採納並執行。
Owner: Ray 拍板 | Claude Code 執行

## D008 - 每日開機日報制度

Date: 2026-06-25
Decision: 今日起所有 Agent 每日開機後必須在 `08_AGENT_OS/[Agent]/DAILY_[Agent]_YYYYMMDD.md` 建立當日日報，收工前更新「昨日達成」欄位。
Reason: 讓一人公司 OS 具備可銜接、可稽核、可跨 Agent 接手的每日工作記錄，避免聊天紀錄成為唯一上下文。
Owner: Ray 拍板 | Codex 落地 | 寫入 AGENT_RULES.md 第十三條
