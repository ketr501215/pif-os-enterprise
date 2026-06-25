# SYNC_STATUS.md
# F Master ↔ Google Drive Mirror ↔ GitHub Version Control

> 每次同步後更新本檔。不允許口頭說「已同步」，必須留實證。

---

## 三層架構

| 層 | 路徑 | 角色 | 同步方向 |
|----|------|------|----------|
| Master | `F:\42-0 一人公司-規劃與運作\PIF_OS\` | 唯一真相來源 | 推出 → |
| Mirror | `Google Drive ketr501218\PIF_OS\` | 雲端鏡像（每日） | ← F 推入 |
| Version | `GitHub: pif-os-enterprise (Private)` | 版本控管（封版才推） | ← F 推入 |

---

## 最後同步紀錄

| 同步時間 | F→Google | F→GitHub | 執行者 | 備註 |
|----------|----------|----------|--------|------|
| 2026-06-25 | ⬜ 待執行 | ⬜ 待建立 | — | GitHub Repo 尚未建立 |

---

## GitHub 初始化步驟（Ray 執行一次）

```powershell
# Step 1：Ray 在 GitHub.com 建立 Private Repo：pif-os-enterprise

# Step 2：本機初始化
cd "F:\42-0 一人公司-規劃與運作\PIF_OS"
git init
git remote add origin https://github.com/[Ray的GitHub帳號]/pif-os-enterprise.git

# Step 3：第一次推送
git add 00_POCC\
git commit -m "feat: POCC v0.1 Sprint 1 Day 1 - foundation files (2026-06-25)"
git push -u origin main
```

---

## 日常同步指令（每次封版後執行）

```powershell
# F → GitHub（封版才推）
cd "F:\42-0 一人公司-規劃與運作\PIF_OS"
git add -A
git commit -m "feat: [描述] (YYYY-MM-DD)"
git push origin main

# F → Google Drive（每日，由 robocopy 或手動）
robocopy "F:\42-0 一人公司-規劃與運作\PIF_OS" "V:\PIF_OS" /MIR /XF *.tmp ~$* /LOG:sync_log.txt
```

---

## 同步驗證方式（不接受「好像同步了」）

```powershell
# 驗證 F ↔ Google 最近修改時間一致
Get-ChildItem "F:\42-0 一人公司-規劃與運作\PIF_OS\00_POCC" -Recurse |
  Select-Object Name, LastWriteTime, Length |
  Sort-Object LastWriteTime -Descending | Select-Object -First 10

# 驗證 GitHub 最新 commit
git log --oneline -5
```

---

## .gitignore 規則（確定版）

```gitignore
# 客戶機密（絕對不推）
客戶資料_Private_Client_Data/
**/CoA/
**/SDS/
**/*配方*
**/*_client_*

# 大型二進位（不納入 git，靠 Google Drive 備份）
*.pdf
*.docx
*.xlsx
*.zip
*.png
*.jpg

# 系統暫存
.DS_Store
Thumbs.db
~$*
*.tmp
__pycache__/
*.pyc
```

---

*SYNC_STATUS.md v0.1 | 2026-06-25 | Claude Code*
