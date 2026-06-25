# PIF OS Control Center（POCC）

> **所有 Agent 的入口。開始工作前必讀此資料夾。**

---

## 這個資料夾是什麼？

POCC（PIF OS Control Center）是整個 PIF OS 的指揮中心。
它不是放 PIF 文件的地方，而是讓所有 Agent 知道：

- 現在系統狀態如何？→ `PROJECT_STATUS.md`
- 我的任務是什麼？→ `TASK_BOARD.md`
- 我該怎麼工作？→ `AGENT_RULES.md`
- 最近改了什麼？→ `CHANGELOG.md`

---

## 所有 Agent 開工 SOP（3 步驟，不可跳過）

```
Step 1：讀 PROJECT_STATUS.md（30 秒，確認系統現況）
Step 2：讀 TASK_BOARD.md（找到自己的任務）
Step 3：讀 AGENT_RULES.md（確認工作規範）
```

---

## 檔案清單

| 檔案 | 用途 | 更新頻率 |
|------|------|----------|
| `PROJECT_STATUS.md` | 系統完成度、當前優先任務、已知 bugs | 每日 |
| `TASK_BOARD.md` | 任務看板（TODO/DOING/REVIEW/DONE/HOLD） | 每次任務更新 |
| `AGENT_RULES.md` | Agent 工作守則（10 條黃金法則） | 重大變更時 |
| `CHANGELOG.md` | 每次封版的變更紀錄 | 每次封版 |
| `README.md` | 本檔，POCC 說明 | 架構變更時 |

---

## PIF OS 系統架構（一眼看清）

```
PIF OS
│
├── 00_POCC/                    ← 你在這裡（指揮中心）
├── 01_Knowledge_OS/            ← 法規 KB / 原料 KB / 功效 KB
├── 02_Document_OS/             ← PIF 生成 / ISO22716
├── 03_Rule_Engine/             ← 法規規則引擎
├── 04_Agent_OS/                ← Agent 協作紀錄
└── 99_Archive/                 ← 封存（不刪除）
```

---

## 版本資訊

- POCC 版本：v0.1
- 建立日：2026-06-25
- Product Owner：Ray
- 執行 Agent：Claude Code
