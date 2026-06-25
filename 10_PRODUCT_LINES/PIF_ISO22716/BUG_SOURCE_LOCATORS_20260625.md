# BUG_SOURCE_LOCATORS_20260625.md
# PIF OS Enterprise — PIF/ISO22716 Product Line
# 主責：Claude Code | 日期：2026-06-25
# 用途：提供 Codex 重抽所需的 PDF 位置與段落定位

---

## 總覽

| BUG-ID | 物質 | 錯值 | 正確值 | 狀態 |
|--------|------|------|--------|------|
| BUG-001 | Chlorphenesin | NOAEL=10（誤取自 LD50 段） | NOAEL=100 | HOLD_CODEX_REEXTRACT |
| BUG-002 | Camellia sinensis | 眼刺激 Non-irritant（方向反轉） | slight ocular irritant | HOLD_CODEX_REEXTRACT |
| BUG-003 | Portulaca oleracea | LD50_oral=1865（實為 dermal 值） | LD50_oral ≤500 | HOLD_CODEX_REEXTRACT |

---

## BUG-001：Chlorphenesin NOAEL 誤抽

### 錯誤記錄
- **來源檔案**：`F:\11-7 ...\DATApool_2_regulatory_staging\cir.json`
- **物質**：Chlorphenesin（INCI: CHLORPHENESIN）
- **錯誤欄位**：`noael`
- **錯誤值**：`10`（mg/kg/day）
- **問題根因**：爬蟲從 LD50 急性致死段落抽取，非來自 NOAEL 重複劑量毒性段落

### 正確值定位
- **正確值**：`100`（mg/kg/day）
- **佐證來源**：Biolume 完整版 PIF p.257（2026-06-13 比對確認）
- **CIR PDF 段落**：應在「Repeated-dose toxicity」或「Subchronic/Chronic toxicity」段，非 LD50 段
- **Codex 重抽指示**：請在 CIR PDF 搜尋 "chlorphenesin" + "NOAEL"，確認段落標題為 subchronic/chronic，排除 LD50 acute lethal 段

### 影響文件
- production `cir.json` 中 Chlorphenesin.noael = 10（已隔離，未 promote）
- 11-7 工作目錄爬蟲快取

---

## BUG-002：Camellia sinensis 眼刺激方向反轉

### 錯誤記錄
- **來源檔案**：`cir.json` staging（camellia 摘要塊）
- **物質**：Camellia sinensis leaf extract
- **錯誤欄位**：`eye_irritation`
- **錯誤值**：`Non-irritant`
- **問題根因**：staging 摘要塊（NTP/EFSA 欄位）與 CIR direct PDF 系統性背離，偏向樂觀
- **發現日**：2026-06-16

### 正確值定位
- **正確值**：`slight ocular irritant`
- **佐證來源**：CIR direct PDF 正文（非摘要塊）
- **Codex 重抽指示**：
  1. 避免使用 staging 摘要塊（已知污染）
  2. 直接讀 CIR official PDF
  3. 搜尋「camellia」+「eye」+「irritat」
  4. 確認 study type 是 rabbit/in vitro 眼刺激正式試驗，非摘要敘述

### 影響評估
- 26-021/26-132/26-136 案眼刺激反向（未出貨）
- MoS 計算不翻盤
- 待 SA 簽核前可修正，衝擊低

---

## BUG-003：Portulaca oleracea LD50_oral 欄位誤植

### 錯誤記錄
- **來源檔案**：`cir.json` 或 tox staging
- **物質**：Portulaca oleracea extract
- **錯誤欄位**：`ld50_oral`
- **錯誤值**：`1865`（mg/kg，實為 dermal 值）
- **問題根因**：oral 與 dermal 欄位混置，爬蟲抓到 dermal LD50 填入 oral 欄
- **發現日**：2026-06-17（校端揪出）

### 正確值定位
- **正確值**：`≤500`（mg/kg，oral）
- **佐證來源**：CIR PDF 正本「Acute toxicity」段，oral LD50 數值
- **Codex 重抽指示**：
  1. 搜尋「portulaca」+「LD50」+「oral」
  2. 確認 route = oral（po / gavage），非 dermal / topical
  3. 若 dermal 值 = 1865 出現，確認其 route 標記，不得填入 oral 欄

### 影響評估
- 同 camellia：零出貨衝擊
- 若 MoS 用 oral LD50 計算，數字偏寬鬆（1865 > 500）→ 修正後 MoS 可能下修

---

## Codex 行動清單（收到本文件後）

```
[ ] 1. 確認三份 CIR PDF 的取得路徑（是否在 DATApool 或需重爬）
[ ] 2. BUG-001 Chlorphenesin：重抽 NOAEL，提供 quote + page no.
[ ] 3. BUG-002 Camellia：重抽 eye_irritation，提供 study type + value + page no.
[ ] 4. BUG-003 Portulaca：重抽 LD50_oral，提供 route 確認 + value + page no.
[ ] 5. 產出 BUG_FIX_PLAN_20260625.md（含修正值 + SA 簽核計畫）
[ ] 6. Claude Code Gate review（只讀最終 Plan，不讀中間過程）
[ ] 7. SA 簽核 + Ray 拍板 → promote
```

---

版本：v0.1
產出人：Claude Code
下一步：等 Codex ACK 並產出 `BUG_FIX_PLAN_20260625.md`
