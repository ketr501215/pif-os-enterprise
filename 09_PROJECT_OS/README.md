# 09_PROJECT_OS

This folder is the shared cross-Agent operating layer.

## Authoritative Shared Files

```text
09_PROJECT_OS/
  WORK_PACKAGE/
  REVIEW/
  DECISION_LOG.md
```

## Rules

- Work package status goes in `WORK_PACKAGE/WPxxx.md`.
- Review output goes in `REVIEW/WPxxx_REVIEW.md`.
- Decisions go only in `DECISION_LOG.md`.
- Agent-to-Agent mailboxes are not used.
- Each Agent keeps only personal `STATUS.md` and daily `DAILY_YYYYMMDD.md` under `08_AGENT_OS/[Agent]/`.

## RayFlow role gates

All agents are additionally bound by repository `AGENTS.md` and
`08_AGENT_OS/RAYFLOW_ROLE_GATE_RULES_v0.1.md`. The normative machine policy is
`SCHEMA/rayflow-role-gates-v0.1.json`; every transition must have a
`rayflow.gate-run/v0.1` record validated through
`TOOLS/Invoke-RoleGate.ps1`.

The communication-location conflict documented by WP001 remains a Critical
HOLD. These role gates add execution controls but do not silently resolve that
conflict.
