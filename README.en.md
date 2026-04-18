# 不客套 bu-ketao

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![繁體中文](https://img.shields.io/badge/lang-Traditional_Chinese-red.svg)](#)
[![Compression](https://img.shields.io/badge/compression-~21--72%25-brightgreen.svg)](#test-results)
[![Claude Code](https://img.shields.io/badge/Claude_Code-skill-blueviolet.svg)](rules/CLAUDE.md)
[![ChatGPT](https://img.shields.io/badge/ChatGPT-compatible-74aa9c.svg)](rules/system-prompt.md)
[![Cursor](https://img.shields.io/badge/Cursor-compatible-000.svg)](rules/cursorrules)

[繁體中文](README.md)

**Strip the 客套 (pleasantries) from Chinese LLM output. ~21-72% compression range, zero semantic loss.**

"bu-ketao" (不客套) literally means "no pleasantries" in Chinese. Chinese LLMs are verbose in fundamentally different ways than English ones — there are no articles (a/an/the) to drop. The fluff has entirely different sources, so the compression rules must be different too.

## The Problem

Ask a Chinese LLM a technical question, and you get:

> **好的，讓我來幫你分析一下這個問題。** 你的組件之所以會頻繁重新渲染，**主要是因為**你在每次渲染時都創建了一個新的物件引用。**簡單來說**，當你把一個 inline object 作為 prop 傳遞時，React 會認為這是一個全新的值，因此觸發重新渲染。**需要注意的是**，這是一個非常常見的效能問題。建議你使用 `useMemo` 來記憶化這個物件，這樣就能避免不必要的重新渲染了。**希望這對你有幫助！**

With bu-ketao:

> inline object prop = 每次新 ref = re-render。`useMemo` 包住。

Same information. ~80% fewer characters.

## Why Chinese Needs Its Own Rules

English compression tools (like [caveman](https://github.com/JuliusBrussee/caveman)) don't work for Chinese:

| English compression lever           | Works in Chinese?                            |
| ----------------------------------- | -------------------------------------------- |
| Drop articles (a/an/the)            | ❌ Don't exist in Chinese                   |
| Drop filler (just/really/basically) | ⚠️ Chinese has different fillers      |
| Abbreviations (DB/auth/config)      | ❌ Chinese is already compact per-character |

We identified **10 textual verbosity patterns + 3 behavioral patterns** specific to Chinese LLMs.

## Chinese AI Verbosity Patterns

### Drop (zero semantic loss)

| Pattern | Examples | Translation |
|---------|---------|-------------|
| **客套話** Pleasantries | 好的，讓我來幫你 / 希望這對你有幫助！ | "OK let me help you" / "Hope this helps!" |
| **填充詞** Filler | 需要注意的是 / 值得一提的是 / 簡單來說 | "It's worth noting that" / "Simply put" |
| **避險語** Hedging | 從某種程度上來說 / 可能需要根據實際情況 | "To some extent" / "Depends on actual situation" |
| **空洞宣稱** Hollow claims | 具有重要意義 / 至關重要的 / 不可或缺的 | "Has significant importance" / "Indispensable" |
| **模糊引用** Phantom attribution | 研究表明... / 有學者認為... (no source) | "Studies show..." / "Scholars believe..." |
| **重複解釋** Repetition | Same point stated 2-3 times in different words | 換句話說... (in other words...) |

### Replace (compress, don't delete)

| Pattern | Compress to |
|---------|-------------|
| 首先...其次...最後...總結 (First...Second...Last...Summary) | Drop ordinals, flat list |
| 由於...因此... (Because...therefore...) | Arrow (→) or direct statement |
| 不僅是 X，更是 Y (Not only X, but also Y) | X 也 Y |
| Template openers (根據分析，我們發現...) | Direct statement |
| Four-character idiom stacking | Keep only necessary ones |

### Behavioral (not rules, but worth knowing)

| Pattern | Example | Real intent |
|---------|---------|-------------|
| **推卸迴避** Scope deflection | "This is a known issue, not in scope" | Avoiding work |
| **催促收工** Conversation escape | "Ready to commit?" / "Should work now" | Rushing to end |
| **主動推銷** Upselling | "I can also help you with something more valuable" | Expanding scope |

## Intensity Levels

| Level | Strategy |
|-------|----------|
| **lite** | Drop pleasantries/filler/hedging. Keep complete sentences |
| **full** | Drop templates, hollow claims, repetition. Fragments OK. One point per sentence |
| **ultra** | Maximum compression, language-agnostic. English when shorter (pool not 連接池). Arrows for causality |

## Test Results

Latest report (2026-04-18) uses a mixed methodology:

- `†`: bidirectional CLI measurement (Before = no bu-ketao rules, After = bu-ketao enabled)
- Others: hypothetical verbose Before baseline (for legacy or prompt-naive outputs)

| Scenario | Domain | Before | After | Compression | Notes |
|----------|--------|--------|-------|-------------|-------|
| Obsidian plugin lifecycle `†` | Technical | ~900 | ~750 | **17%** | Similar structure |
| TypeScript build vs IDE `†` | Technical | ~1,050 | ~900 | **14%** | After adds 2 diagnostics |
| Git rebase conflicts | Technical | ~2,800 | ~800 | 71% | Hypothetical Before |
| Docker OOMKilled debugging | Technical | ~2,200 | ~900 | 59% | Hypothetical Before |
| CSS flexbox vs grid | Technical | ~1,800 | ~500 | 72% | Hypothetical Before |
| Python GIL explained | Technical | ~2,400 | ~550 | 77% | Hypothetical Before |
| OAuth 2.0 Flow `†` | Technical | ~1,300 | ~1,400 | **-8%** | After is longer |
| React 18 useEffect | Technical | ~1,800 | ~250 | 79% | Hypothetical Before |
| MongoDB vs PostgreSQL | Technical | ~2,000 | ~300 | 71% | Hypothetical Before |
| Nginx WebSocket proxy `†` | Technical | ~1,100 | ~600 | **45%** | After is tighter |
| Payment reminder email `†` | Business | ~950 | ~500 | **47%** | Removes framing/table |
| p-value explanation | Academic | ~1,400 | ~450 | 65% | Hypothetical Before |
| Taipei 3D2N itinerary | Lifestyle | ~1,500 | ~500 | 75% | Hypothetical Before |
| Refusing overtime | Workplace | ~1,300 | ~350 | 75% | Hypothetical Before |

Observed in latest runs:

1. Modern `claude-sonnet-4-6` is already concise without rules, so real CLI compression is lower than early assumptions.
2. bu-ketao is not hard truncation. If Before is already concise (OAuth case), After can be longer but more complete.
3. Non-technical writing still shows clear gains (for example payment reminder email).

Full before/after: [`examples/before-after.md`](examples/before-after.md)

### Cost Estimate

Estimated with Claude Sonnet output pricing ($15/M tokens):

| | tokens | cost |
|---|---|---|
| 5 CLI pairs Before (est.) | ~1,355 | $0.020 |
| 5 CLI pairs After (est.) | ~1,065 | $0.016 |
| **Saved on 5 CLI pairs** | **~290** | **$0.004** |
| Extrapolated 14 Before (est.) | ~3,800 | $0.057 |
| Extrapolated 14 After (est.) | ~3,000 | $0.045 |
| **Saved on extrapolated 14** | **~800** | **$0.012** |

### Token Economics

Chinese characters cost more tokens than English in most tokenizers:

| Tokenizer | Chinese token tax (vs same-semantics English) |
|-----------|-----------------------------------------------|
| GPT-4 | 4.94x |
| GPT-4o | 3.38x |
| Claude | ~3-4x (estimated) |
| Qwen2.5 | 2.62x |

**Every Chinese character you cut saves more tokens than cutting an English word.** The ROI of Chinese compression is higher than English.

## Usage

### One-click Install Scripts

Two scripts cover common install paths for AI tools.

Risk notice:
- Running `bash <(curl ...)` directly has supply chain risk. If the downloaded content is tampered with, it can write malicious instructions into local AI config files.
- Prefer download-then-run, inspect the script first, and pin to a commit URL or verify SHA256 in production environments.
- `install-commadns.sh` overwrites existing target files. Back up customized commands before running it.

#### Install Agents Rules (CLAUDE.md / AGENTS.md)

Applicable: Claude Code, Copilot Coding Agent, Codex, Cursor, Kiro

```bash
# Run from remote (convenient, higher risk)
bash <(curl -fsSL https://raw.githubusercontent.com/lazyjerry/bu-ketao/refs/heads/main/install-script/install-agents.sh)
```

```bash
# Or download first (recommended)
curl -fsSL https://raw.githubusercontent.com/lazyjerry/bu-ketao/refs/heads/main/install-script/install-agents.sh -o install-agents.sh
bash install-agents.sh
```

#### Install Slash Command (bu-ketao.md)

Applicable: Claude Code, Copilot, Codex, Cursor, Kiro

```bash
# Run from remote (convenient, higher risk)
bash <(curl -fsSL https://raw.githubusercontent.com/lazyjerry/bu-ketao/refs/heads/main/install-script/install-commadns.sh)
```

```bash
# Or download first (recommended)
curl -fsSL https://raw.githubusercontent.com/lazyjerry/bu-ketao/refs/heads/main/install-script/install-commadns.sh -o install-commadns.sh
bash install-commadns.sh
```

### Claude Code — Global Rules (CLAUDE.md)

Copy or symlink [`rules/CLAUDE.md`](rules/CLAUDE.md) to `~/.claude/CLAUDE.md` for automatic compression in all Claude Code sessions:

```bash
# Copy
cp rules/CLAUDE.md ~/.claude/CLAUDE.md

# Or symlink (auto-updates with project)
ln -sf "$(pwd)/rules/CLAUDE.md" ~/.claude/CLAUDE.md
```

### Claude Code — Slash Command

Copy [`commands/bu-ketao.md`](commands/bu-ketao.md) to `~/.claude/commands/bu-ketao.md` for on-demand activation with intensity levels:

```bash
cp commands/bu-ketao.md ~/.claude/commands/bu-ketao.md
```

```
/bu-ketao          # default: full
/bu-ketao lite     # professional, concise
/bu-ketao ultra    # maximum compression
```

### GitHub Copilot — Coding Agent (AGENTS.md)

Copy [`rules/AGENTS.md`](rules/AGENTS.md) to any repo root for automatic Copilot Coding Agent integration:

```bash
cp rules/AGENTS.md /path/to/your/project/AGENTS.md
```

### GitHub Copilot — Skill

Recommended: install with [`ai-global`](https://github.com/lazyjerry/ai-global):

```bash
ai-global add lazyjerry/bu-ketao
```

Or copy or symlink [`skill/bu-ketao/`](skill/bu-ketao/) to `~/.copilot/skills/` for cross-repo auto-detection:

```bash
# Copy
cp -r skill/bu-ketao ~/.copilot/skills/bu-ketao

# Or symlink
ln -sf "$(pwd)/skill/bu-ketao" ~/.copilot/skills/bu-ketao
```

### ChatGPT / Claude / Gemini (system prompt)

Paste [`rules/system-prompt.md`](rules/system-prompt.md) content into your system prompt. Works with any LLM that accepts system instructions.

### Cursor

Copy [`rules/cursorrules`](rules/cursorrules) to `.cursorrules` in your project root.

## Related Projects

| Project | Approach | vs bu-ketao |
|---------|----------|-------------|
| [caveman](https://github.com/JuliusBrussee/caveman) | English output compression (drop articles, abbreviations) | English rules don't work for Chinese; wenyan = Classical Chinese stylization, not practical compression |
| [cjk-token-reducer](https://github.com/jserv/cjk-token-reducer) | Translate CJK input to English before sending to LLM | Compresses **input** (translate prompts); bu-ketao compresses **output** (less AI fluff). Complementary |
| [LLMLingua](https://github.com/microsoft/LLMLingua) | Perplexity-based token removal | General prompt compression, not Chinese-specific; input-side only |
| [prompt-optimizer](https://github.com/linshenkx/prompt-optimizer) | Chinese prompt optimizer (25k+ stars) | Makes AI answer *better*, not *shorter* |

**bu-ketao's unique position**: no other project systematically catalogs Chinese AI output verbosity patterns and provides ready-to-use compression rulesets.

bu-ketao's rules are also [proposed upstream to caveman](https://github.com/JuliusBrussee/caveman/pull/160) as `zh-tw-lite/full/ultra` modes.

## License

MIT
