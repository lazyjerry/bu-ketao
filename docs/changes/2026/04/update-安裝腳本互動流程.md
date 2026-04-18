# 更新安裝腳本互動流程

## 結論
已完成 [install-script/install-agents.sh](install-script/install-agents.sh) 的互動式安裝流程，支援安裝位置與檔案類型選擇，並在偵測到既有 bu-ketao 內容時略過附加，避免重複安裝。

## 問題分析
原本 [install-script/install-agents.sh](install-script/install-agents.sh) 為空檔，尚未提供以下能力：
- 讓使用者選擇安裝於專案目錄或全域位置
- 讓使用者選擇安裝 AGENTS.md 或 CLAUDE.md
- 依照不同目標路徑執行建立或附加
- 偵測既有檔案中的 bu-ketao 字樣並略過

## 解決方案
以 Bash 實作完整流程，重點如下：
- 以互動式選單提供兩項選擇：
  - 安裝位置：專案目錄或全域位置（預設全域）
  - 安裝檔案：AGENTS.md、CLAUDE.md 或兩者
- 從 GitHub raw URL 下載來源文件到暫存目錄
- 專案模式：
  - 優先使用 git 專案根目錄；若非 git 專案則以目前資料夾為根目錄
  - 目標為專案根目錄下的 AGENTS.md 或 CLAUDE.md
- 全域模式：
  - CLAUDE.md：~/.claude/CLAUDE.md
  - AGENTS.md：~/.codex/AGENTS.md、~/.copilot/AGENTS.md、~/.cursor/AGENTS.md、~/.kiro/AGENTS.md
- 目標資料夾不存在時僅提示並略過；資料夾存在且檔案不存在則建立；檔案存在則附加到尾端
- 既有檔案若含有 bu-ketao 字樣，提示「目前偵測到『bu-ketao』字樣，請確認是否已經安裝？」並略過該檔案

## 變更內容
- 🔄 變更檔案：
  - [install-script/install-agents.sh](install-script/install-agents.sh)
- 🆕 新增檔案：
  - [docs/changes/2026/04/update-安裝腳本互動流程.md](docs/changes/2026/04/update-安裝腳本互動流程.md)

### 2026-04-18 調整
- 安裝來源改為單一網址：`CLAUDE_URL`
- 移除「選擇安裝 AGENTS.md 或 CLAUDE.md」互動流程
- 需要安裝 AGENTS.md 的位置時，改用下載後的 CLAUDE.md 內容直接建立或附加到 AGENTS.md
- 專案模式固定處理專案根目錄下的 CLAUDE.md 與 AGENTS.md
- 全域模式固定處理 ~/.claude/CLAUDE.md 與各工具目錄的 AGENTS.md

關鍵函式與流程：
- `prompt_install_scope`：安裝位置互動選擇（預設全域）
- `prompt_install_files`：安裝檔案互動選擇
- `download_sources`：下載 AGENTS.md 與 CLAUDE.md
- `detect_project_root`：偵測專案根目錄
- `contains_bu_ketao`：檢查目標檔案是否含 bu-ketao
- `install_into_file`：執行建立或附加，並在命中關鍵字時略過
- `install_for_project_scope` / `install_for_global_scope`：依模式套用目標路徑

## 注意事項
**向下相容性：**
- 不變更既有外部介面，僅新增 [install-script/install-agents.sh](install-script/install-agents.sh) 內容
- 腳本依賴 `curl`，若環境缺少 `curl` 會中止並提示

**潛在錯誤：**
- 網路連線異常或 URL 無法存取時，下載步驟會失敗並中止
- 目標檔案無寫入權限時，建立或附加會失敗

**使用體驗影響：**
- 使用者需在互動流程中做兩次選擇，完成後會逐一顯示各目標處理結果
- 全域模式僅處理既有資料夾，不會主動建立缺少的工具資料夾
