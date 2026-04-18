# 不客套 bu-ketao

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![繁體中文](https://img.shields.io/badge/語言-繁體中文-red.svg)](#)
[![壓縮率](https://img.shields.io/badge/壓縮率-~21--72%25-brightgreen.svg)](#實測數據)
[![Claude Code](https://img.shields.io/badge/Claude_Code-skill-blueviolet.svg)](rules/CLAUDE.md)
[![ChatGPT](https://img.shields.io/badge/ChatGPT-compatible-74aa9c.svg)](rules/system-prompt.md)
[![Cursor](https://img.shields.io/badge/Cursor-compatible-000.svg)](rules/cursorrules)
[![Copilot](https://img.shields.io/badge/Copilot-compatible-1f6feb.svg)](rules/AGENTS.md)

[English](README.en.md)

**砍掉中文 AI 的客套問候話，留下乾貨。**

中文 LLM 的囉唆跟英文完全不同 —— 英文靠砍冠詞（a/an/the）就能省很多，但中文根本沒有冠詞。廢話的來源不一樣，壓縮的方式也該不一樣。

## 問題

問一個技術問題，中文 AI 回你這個：

> **好的，讓我來幫你分析一下這個問題。** 你的組件之所以會頻繁重新渲染，**主要是因為**你在每次渲染時都創建了一個新的物件引用。**簡單來說**，當你把一個 inline object 作為 prop 傳遞時，React 會認為這是一個全新的值，因此觸發重新渲染。**需要注意的是**，這是一個非常常見的效能問題。建議你使用 `useMemo` 來記憶化這個物件，這樣就能避免不必要的重新渲染了。**希望這對你有幫助！**

用不客套壓縮後：

> inline object prop = 每次新 ref = re-render。`useMemo` 包住。

同樣的資訊，少 80% 的字。

## 為什麼中文需要自己的規則

英文壓縮工具（如 [caveman](https://github.com/JuliusBrussee/caveman)）的核心手段套到中文完全不太實用：

| 英文壓縮手段                     | 對中文有用？        |
| -------------------------- | ------------- |
| 砍冠詞 a/an/the               | ❌ 中文沒有冠詞      |
| 砍填充詞 just/really/basically | ⚠️ 中文有不同的填充詞  |
| 縮寫 DB/auth/config          | ❌ 中文本身每個字就很緊湊 |

中文 AI 的廢話有自己的結構，我們歸納出 **14 類文字冗餘 + 3 類行為冗餘**。

## 中文 AI 客服腔完整詞庫

### 砍除類（Drop）— 刪掉零語義損失

#### 客套話

| 位置 | 廢話 |
|------|------|
| 開場 | 好的 / 當然 / 讓我來幫你分析一下 / 我來為你詳細解釋 |
| 結尾 | 希望這對你有幫助 / 歡迎繼續提問 / 如果你還有其他問題 / 歡迎隨時提問 |
| 過渡 | 接下來讓我們看看 / 讓我進一步說明 |

#### 填充詞

> 需要注意的是 / 值得一提的是 / 值得注意的是 / 一般來說 / 通常來說 / 簡單來說 / 具體來說 / 事實上 / 基本上 / 實際上 / 坦白說 / 嚴格來說

這些詞刪掉後，後面的句子意思完全不變。

#### 避險語

> 從某種程度上來說 / 可能需要根據實際情況調整 / 這只是我的建議 / 具體情況可能因環境而異 / 建議在正式環境中先進行測試

AI 用這些語句甩責。在技術回答中，如果你確定就直接說，不確定就明講哪裡不確定。

#### 空洞宣稱

> 具有重要意義 / 至關重要的 / 不可或缺的 / 前所未有的 / 具有深遠的影響 / 具有里程碑意義

連一個購物中心都能被 AI 描述成「文化遺產的中心」。砍。

#### 模糊引用

> 研究表明... / 有學者認為... / 根據最佳實踐... / 已有文獻指出...

沒有具體出處的引用 = 虛構的權威感。要嘛給來源，要嘛別提。

#### 重複解釋

中文 LLM 最嚴重的問題：同一件事用 2-3 種方式說。

> 連接池會重複使用已建立的連接。**換句話說**，它維護一組現成的連接，避免重複建立。**也就是說**，不用每次都從頭連線。

三句話講的是同一件事。砍到剩一句。

#### 總結印章

> 一句話總結：... / 總而言之 / 簡而言之 / 概括來說

直接講結論，不要貼「這是結論」的標籤。

#### 覆述問題

用戶問「React 為什麼 re-render」，AI 開頭回「你問的是 React component 為什麼會重新渲染這個問題...」。用戶知道自己問了什麼，不需要 AI 複讀。

#### 條件式推銷

> 如果你告訴我你的環境，我可以給更具體的建議 / 如果你願意，我下一步可以幫你...

推銷的隱蔽變體。回答完就停，有具體下一步就直接講，不要包條件句。

#### 白話翻譯區塊

> 翻成人話就是... / 用白話說... / 簡單來說就是...

先用技術語言解釋一遍，再開一個「降維解釋」區塊重述同一件事。一次講清楚就好。

### 替換類（Replace）— 壓縮不刪除

| 原文 | 壓縮為 |
|------|--------|
| 首先...其次...再者...最後...總結來說 | 去掉序號，直接列點 |
| 由於...因此... | 箭頭（→）或直述 |
| 不僅是 X，更是 Y | X 也 Y |
| 根據分析，我們發現... | 直述結果 |
| 四字成語堆砌（循序漸進、行之有效、與日俱增） | 只保留必要的 |
| 被動語態（可以被認為是） | 改主動語態 |
| 「從 X 到 Y」虛假範圍修辭 | 直述具體內容 |
| 不是 X，而是 Y（否定對比框架） | 直述 Y。❌「真正的問題不是效能，而是架構」→ ✅「真正的問題是架構」 |
| 比較題寫平衡論文 | 直接給推薦 + 簡短理由，每邊最多 3-4 點。不要列完優缺點說「看你需求」 |

### 行為類（觀察，不進壓縮規則）

除了文字冗餘，中文 LLM 還有行為層面的廢話：

| 行為 | 範例 | 真實意圖 |
|------|------|---------|
| **推卸迴避** | 「這是之前就知道的問題，不在這次範圍之內」 | 不想做 |
| **催促收工** | 「可以 commit 了嗎？」「目前修改已經可以正常運作了」 | 想結束對話 |
| **主動推銷** | 「如果你願意，我可以幫你做一件更有價值的事」 | 膨脹 scope |

這些是行為問題，不是文字問題，所以不放進壓縮規則。但知道它們存在有助於辨識 AI 的意圖。

## 三個等級

| 等級 | 策略 | 適合場景 |
|------|------|---------|
| **lite** | 砍客套/填充/避險，保留完整句子 | 正式文件、給非工程師看的回答 |
| **full** | 砍模板句、空洞宣稱、重複解釋。碎片句 OK，一重點一句 | 日常開發對話（預設） |
| **ultra** | 最大壓縮，語言無關——英文更短就用英文（pool not 連接池）。箭頭因果、縮寫 | 快速 debug、context 吃緊時 |

### 等級對比範例

**問題**：「為什麼 React component 會 re-render？」

**原始（AI 客服腔）**：
> 好的，讓我來幫你分析一下這個問題。你的組件之所以會頻繁重新渲染，主要是因為你在每次渲染時都創建了一個新的物件引用。簡單來說，當你把一個 inline object 作為 prop 傳遞時，React 會認為這是一個全新的值，因此觸發重新渲染。需要注意的是，這是一個非常常見的效能問題。建議你使用 `useMemo` 來記憶化這個物件，這樣就能避免不必要的重新渲染了。希望這對你有幫助！

**lite**：
> 組件頻繁重新渲染，因為每次渲染都創建新的物件引用。inline object prop 每次都是新 reference，觸發 re-render。用 `useMemo` 包住即可。

**full**：
> inline object prop = 每次新 ref = re-render。`useMemo` 包住。

**ultra**：
> inline obj prop → new ref → re-render。`useMemo`。

## 實測數據

最新報告（2026-04-18）改為「CLI 雙向實測 + 假設性對比」混合標註：

- `†`：CLI 雙向實測（Before = 無規則，After = bu-ketao）
- 其餘：假設性 Before（對照傳統臃腫輸出）

| 情境 | 領域 | Before | After | 壓縮率 | 備註 |
|------|------|--------|-------|--------|------|
| Obsidian plugin 生命週期 `†` | 技術 | ~900 | ~750 | **17%** | 兩版結構相近 |
| TypeScript build vs IDE `†` | 技術 | ~1,050 | ~900 | **14%** | After 多了 2 個排查點 |
| Git rebase 衝突 | 技術 | ~2,800 | ~800 | 71% | 假設性 Before |
| Docker OOMKilled 排查 | 技術 | ~2,200 | ~900 | 59% | 假設性 Before |
| CSS flexbox vs grid | 技術 | ~1,800 | ~500 | 72% | 假設性 Before |
| Python GIL 解釋 | 技術 | ~2,400 | ~550 | 77% | 假設性 Before |
| OAuth 2.0 Flow `†` | 技術 | ~1,300 | ~1,400 | **-8%** | After 比 Before 更長 |
| React 18 useEffect | 技術 | ~1,800 | ~250 | 79% | 假設性 Before |
| MongoDB vs PostgreSQL | 技術 | ~2,000 | ~300 | 71% | 假設性 Before |
| Nginx WebSocket proxy `†` | 技術 | ~1,100 | ~600 | **45%** | After 更精簡 |
| 催款郵件 `†` | 商業 | ~950 | ~500 | **47%** | After 去掉表格與前言 |
| p-value 解釋 | 學術 | ~1,400 | ~450 | 65% | 假設性 Before |
| 台北三天兩夜行程 | 生活 | ~1,500 | ~500 | 75% | 假設性 Before |
| 拒絕加班 | 職場 | ~1,300 | ~350 | 75% | 假設性 Before |

實測觀察：

1. 現代 `claude-sonnet-4-6` 在無規則時已比過去精簡，CLI 實測壓縮率低於早期假設值。
2. bu-ketao 不是硬性截短；當 Before 已精簡時（如 OAuth），After 可能更完整而變長。
3. 非技術情境（如催款信）仍有明顯壓縮收益。

Token 計算使用 cl100k_base tokenizer（GPT-4/Claude 系列）。

完整 before/after 對比：[`examples/before-after.md`](examples/before-after.md)

### 成本換算

以 Claude Sonnet output 定價 $15/M tokens 估算：

| | tokens | 成本 |
|---|---|---|
| CLI 實測 5 組 Before（估） | ~1,355 | $0.020 |
| CLI 實測 5 組 After（估） | ~1,065 | $0.016 |
| **CLI 實測 5 組省下** | **~290** | **$0.004** |
| 推算 14 組 Before（估） | ~3,800 | $0.057 |
| 推算 14 組 After（估） | ~3,000 | $0.045 |
| **推算 14 組省下** | **~800** | **$0.012** |

### Token 經濟學

中文字在大部分 tokenizer 裡都比英文貴：

| Tokenizer | 中文 token 稅（vs 同語義英文） |
|-----------|-------------------------------|
| GPT-4 | 4.94x |
| GPT-4o | 3.38x |
| Claude | ~3-4x（估計） |
| Qwen2.5 | 2.62x |

**砍一個中文廢話字，省的 token 比砍一個英文廢話詞還多。** 中文壓縮的 ROI 比英文更高。

## 使用方式

### 一鍵安裝腳本

提供兩支腳本，覆蓋常見 AI 工具的安裝路徑，執行後依照提示選擇安裝位置即可。

風險提示：
- 遠端直接執行 `bash <(curl ...)` 有供應鏈風險。若下載來源遭竄改，惡意內容會直接寫入 AI 工具設定檔。
- 建議先下載腳本再執行，並先檢查內容；正式環境建議固定 commit 版本（pin）或加入 SHA256 校驗。
- `install-commadns.sh` 會覆蓋既有目標檔案；若你有自訂 command，請先備份。

#### 安裝 Agents 規範（CLAUDE.md / AGENTS.md）

適用：Claude Code、Copilot Coding Agent、Codex、Cursor、Kiro

```bash
# 遠端直接執行（推薦）
bash <(curl -fsSL https://raw.githubusercontent.com/lazyjerry/bu-ketao/refs/heads/main/install-script/install-agents.sh)
```

```bash
# 或先下載再執行
curl -fsSL https://raw.githubusercontent.com/lazyjerry/bu-ketao/refs/heads/main/install-script/install-agents.sh -o install-agents.sh
bash install-agents.sh
```

執行後選擇安裝位置：
- `1` — 專案目錄（寫入目前 git repo 根目錄）
- `2` — 全域位置（預設，寫入 `~/.claude/`、`~/.copilot/`、`~/.cursor/` 等）

#### 安裝 Slash Command（bu-ketao.md）

適用：Claude Code、Copilot、Codex、Cursor、Kiro

```bash
# 遠端直接執行（推薦）
bash <(curl -fsSL https://raw.githubusercontent.com/lazyjerry/bu-ketao/refs/heads/main/install-script/install-commadns.sh)
```

```bash
# 或先下載再執行
curl -fsSL https://raw.githubusercontent.com/lazyjerry/bu-ketao/refs/heads/main/install-script/install-commadns.sh -o install-commadns.sh
bash install-commadns.sh
```

腳本自動偵測 `~/.claude/commands/`、`~/.copilot/commands/`、`~/.cursor/commands/`、`~/.codex/commands/`、`~/.kiro/prompts/` 並安裝到所有已存在的目錄。

---

### Claude Code — 全域規範（CLAUDE.md）

把 [`rules/CLAUDE.md`](rules/CLAUDE.md) 複製或 symlink 到 `~/.claude/CLAUDE.md`，所有 Claude Code 對話自動套用壓縮：

```bash
# 複製
cp rules/CLAUDE.md ~/.claude/CLAUDE.md

# 或 symlink（隨專案更新）
ln -sf "$(pwd)/rules/CLAUDE.md" ~/.claude/CLAUDE.md
```

### Claude Code — Slash Command

把 [`commands/bu-ketao.md`](commands/bu-ketao.md) 複製到 `~/.claude/commands/bu-ketao.md`，手動觸發並支援等級切換：

```bash
cp commands/bu-ketao.md ~/.claude/commands/bu-ketao.md
```

```
/bu-ketao          # 預設 full
/bu-ketao lite     # 專業簡潔
/bu-ketao ultra    # 最大壓縮
```

### GitHub Copilot — Coding Agent（AGENTS.md）

把 [`rules/AGENTS.md`](rules/AGENTS.md) 放在任何 repo 根目錄，Copilot Coding Agent 自動套用：

```bash
cp rules/AGENTS.md /path/to/your/project/AGENTS.md
```

### GitHub Copilot — Skill

推薦用 [`ai-global`](https://github.com/lazyjerry/ai-global) 一鍵安裝：

```bash
ai-global add lazyjerry/bu-ketao
```

或手動把 [`skill/bu-ketao/`](skill/bu-ketao/) 複製或 symlink 到 `~/.copilot/skills/`，Copilot Chat 跨 repo 自動偵測觸發：

```bash
# 複製
cp -r skill/bu-ketao ~/.copilot/skills/bu-ketao

# 或 symlink
ln -sf "$(pwd)/skill/bu-ketao" ~/.copilot/skills/bu-ketao
```

### ChatGPT / Claude / Gemini（system prompt）

把 [`rules/system-prompt.md`](rules/system-prompt.md) 的內容貼進 system prompt。適用任何支援 system instructions 的 LLM。

### ChatGPT Custom Instructions / GPTs

把 [`rules/openai-custom-instructions.md`](rules/openai-custom-instructions.md) 的內容貼進 ChatGPT 的 Custom Instructions 或 GPTs 的 system prompt。針對 OpenAI 的 token 上限精簡過。

### Cursor

把 [`rules/cursorrules`](rules/cursorrules) 複製到專案根目錄的 `.cursorrules`。

## 相關專案

| 專案 | 做法 | 與不客套的差異 |
|------|------|---------------|
| [caveman](https://github.com/JuliusBrussee/caveman) | 英文 LLM 輸出壓縮（砍冠詞、縮寫） | 英文規則套中文沒用；wenyan 模式是文言文風格化，非實用壓縮 |
| [talk-normal](https://github.com/hexiecs/talk-normal) | 任意 LLM 去 AI slop，中英雙語 | 範圍較廣但中文規則較淺；不客套的繁中冗餘分類（14 類）更深入，有 before/after 實測 |
| [cjk-token-reducer](https://github.com/jserv/cjk-token-reducer) | 把 CJK 輸入翻成英文再送 LLM，省 35-50% input token | 壓的是**輸入端**（翻譯 prompt），不客套壓的是**輸出端**（讓 AI 少廢話）。兩者可互補 |
| [LLMLingua](https://github.com/microsoft/LLMLingua) | 用小模型計算困惑度，移除低資訊量 token | 通用 prompt 壓縮，非針對中文客服腔；壓輸入不壓輸出 |
| [prompt-optimizer](https://github.com/linshenkx/prompt-optimizer) | 中文 prompt 優化器（25k+ stars） | 重點在「讓 AI 回答更好」，不是「讓 AI 回答更短」 |


不客套的規則也已[提交到 caveman 上游](https://github.com/JuliusBrussee/caveman/pull/160)作為 `zh-tw-lite/full/ultra` 模式。

## 檔案結構

```
bu-ketao/
├── README.md                           ← 你在讀的這份（繁體中文）
├── README.en.md                        ← English version
├── LICENSE                             ← MIT
├── commands/
│   └── bu-ketao.md                     ← Claude Code slash command（→ ~/.claude/commands/）
├── skill/
│   └── bu-ketao/
│       └── SKILL.md                    ← Copilot Skill（→ ~/.copilot/skills/）
├── rules/
│   ├── CLAUDE.md                       ← Claude Code 全域規範（→ ~/.claude/CLAUDE.md）
│   ├── AGENTS.md                       ← Copilot Coding Agent 規範（放 repo 根目錄）
│   ├── system-prompt.md                ← 通用 system prompt（SSOT）
│   ├── cursorrules                     ← Cursor 格式
│   └── openai-custom-instructions.md   ← ChatGPT / GPTs 格式
├── examples/
│   └── before-after.md                 ← 完整實測 before/after
└── docs/
    └── report/
```

## 授權

MIT
