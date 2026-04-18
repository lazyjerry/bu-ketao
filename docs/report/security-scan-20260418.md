```
╔══════════════════════════════════════════════════════╗
║           AI 工具 資安掃描報告                       ║
╠══════════════════════════════════════════════════════╣
║  掃描時間：2026-04-18                                ║
║  掃描範圍：當前工作區                                ║
║            /Users/lazyjerry/Dropbox/個人project/     ║
║            個人用專案/bu-ketao                       ║
║  掃描項目：1 skills, 0 agents, 1 commands,           ║
║            5 rules, 1 agents_md, 2 shell scripts     ║
╚══════════════════════════════════════════════════════╝
```

## 風險摘要

| 嚴重性   | 數量 |
|---------|------|
| Critical | 0 |
| High     | 0 |
| Medium   | 1 |
| Low      | 0 |
| 諮詢建議（Advisory） | 1 |

---

## 各項目掃描結果

### ✅ `skill/bu-ketao/SKILL.md`（無問題）
- 僅描述繁中 LLM 壓縮行為，無提示注入、指令注入、資料外洩等疑慮。
- description 與內容高度一致，E2 無觸發。

### ✅ `commands/bu-ketao.md`（無問題）
- 功能邊界清晰，無惡意模式。

### ✅ `rules/CLAUDE.md`（無問題）

### ✅ `rules/copilot-instructions.md`（無問題）

### ✅ `rules/cursorrules`（無問題）

### ✅ `rules/openai-custom-instructions.md`（無問題）

### ✅ `rules/system-prompt.md`（無問題）

---

### ⚠️ `install-script/install-agents.sh`（發現風險）

**[Medium] D3 - 修改 AI 助手設定（預期用途，已知風險）**
- 位置：`install_for_global_scope()`、`install_for_project_scope()`
- 內容：寫入 `~/.claude/CLAUDE.md`、`~/.copilot/AGENTS.md`、`~/.codex/AGENTS.md`、`~/.cursor/AGENTS.md`、`~/.kiro/AGENTS.md`
- 說明：此腳本為安裝程式，修改多個 AI 工具的全域設定檔屬**預期行為**。但須注意：若使用者未檢查下載內容即執行，且 GitHub 倉庫遭入侵，惡意指令可能被注入各 AI 工具的系統設定中。

**[Advisory] 供應鏈風險 — 無完整性驗證**
- 位置：第 5 行 `CLAUDE_URL=...`、`download_sources()` 函數
- 內容：`curl -fsSL "$CLAUDE_URL" -o "$tmp_dir/CLAUDE.md"` 後直接寫入 AI 設定
- 說明：從 GitHub raw URL 下載內容時，**無 SHA256 校驗和或 GPG 簽章驗證**。若 GitHub 帳號遭入侵或遭 MITM 攻擊，下載的 CLAUDE.md 可能含有提示注入指令（A1、A2 類型），且會被自動寫入 `~/.claude/CLAUDE.md` 等高權限位置。
- 建議：在腳本中加入預期的 SHA256 校驗，或提示使用者先以瀏覽器預覽內容後再確認安裝。

### ⚠️ `install-script/install-commadns.sh`（發現風險）

**[Advisory] 供應鏈風險 — 無完整性驗證 + 靜默覆蓋**
- 位置：`download_source()`、`install_command()` 函數
- 內容：下載 command 後，若目標已存在直接 `cp`（覆蓋），無提示
- 說明：同上供應鏈風險，且此腳本會**靜默覆蓋**已存在的 command 檔案，使用者的自訂修改將遺失。`install-agents.sh` 在覆蓋前有 `bu-ketao` 關鍵字偵測；`install-commadns.sh` 無此保護。

---

## 總結建議

1. **現有 skill / rules / commands 內容全數通過掃描**，無任何 A–F 規則違反。
2. **安裝腳本**屬可信用途，但建議加入完整性驗證以防供應鏈攻擊：
   ```bash
   # 在下載後加入校驗範例
   EXPECTED_SHA256="<預期的雜湊值>"
   echo "$EXPECTED_SHA256  $tmp_dir/CLAUDE.md" | sha256sum -c -
   ```
3. `install-commadns.sh` 建議在覆蓋前顯示 diff 或提示確認，與 `install-agents.sh` 的保護邏輯保持一致。

> ⚠️ **提醒**：本報告由 AI 自動產生，結果可能存在誤判（false positive）或遺漏（false negative）。所有發現皆需經人工核實與驗證，不應作為唯一的安全評估依據。
