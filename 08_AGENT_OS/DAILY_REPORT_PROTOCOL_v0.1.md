# Daily Report Protocol v0.1

Date: 2026-06-25
Status: Active
Authority: AGENT_RULES.md Article 13 / Decision D008

## Location Rule

Each Agent must keep its daily report under its own folder:

```text
08_AGENT_OS/[Agent]/DAILY_[Agent]_YYYYMMDD.md
```

## Daily Startup Checklist

1. Read `00_POCC/PROJECT_STATUS.md`.
2. Read `00_POCC/TASK_BOARD.md`.
3. Read `00_POCC/CHANGELOG.md`.
4. Read own latest daily report if it exists.
5. Create today's daily report.
6. Start work only after recording today's owner/task/status.

## Daily Closeout Checklist

1. Update `昨日達成` with work completed since the last startup/closeout.
2. Update `今日已完成`.
3. Mark `收工狀態` as `CLOSED`, `OPEN`, or `HOLD`.
4. Record latest Git commit / sync status when applicable.
5. If another Agent must continue, write the exact file and next action.

## Current Priority Board

| 序 | 子系統 | 優先 | Why |
|---:|---|---|---|
| 1 | 法規知識庫 | P0 | 系統根源；錯誤限量基準會污染所有 MoS / Gate |
| 2 | 原料/功效知識庫 | P0 parallel | 依賴法規 KB，但資料填充可同步推進 |
| 3 | 文件管理系統 | P1 | 目前可運作但需優化 |
| 4 | 版期管理/備份 | P2 | Git/GitHub 已運作；Google Drive mirror 仍待驗證 |

## Template

```markdown
# DAILY_[Agent]_YYYYMMDD

- Agent:
- 日期:
- 開機時間:
- 今日主責:
- 昨日達成:
- 今日目標:
- 今日已完成:
- 今日阻塞:
- 需其他 Agent 接手:
- 收工狀態: OPEN / CLOSED / HOLD
- GitHub / Sync 狀態:
```
