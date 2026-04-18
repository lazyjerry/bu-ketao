# Before / After 實測對比

10 組技術開發情境 + 4 組非技術情境，用 Claude CLI (`claude -p`) 雙向實測。
- **Before [CLI 實測]**：2026-04-18，無 bu-ketao 規則，`claude-sonnet-4-6` 直接回應
- **After [CLI 實測]**：2026-04-18，CLAUDE.md 載入 bu-ketao 規則後的回應

> **重要發現**：原始文件的 Before 範例為假設性臃腫輸出。實測顯示現代 `claude-sonnet-4-6` 不帶規則已相當精簡，bu-ketao 的實際壓縮幅度比預估小，但仍有效果。

---

## 情境 1：Obsidian plugin 生命週期

**問題**：Obsidian plugin 開發中，onLayoutReady 和 onload 有什麼差別？什麼時候該用哪個？

### Before [CLI 實測]（無 bu-ketao，~900 字）

> **`onload` vs `onLayoutReady`**
>
> **`onload`**
> Plugin 的生命週期入口點，在 Obsidian **載入 plugin 時立即執行**，但此時 workspace layout 可能尚未完全初始化。
>
> 適合做：
> - 註冊 commands、ribbon icon、settings tab
> - 註冊 event listener（`this.registerEvent(...)`）
> - 初始化 plugin 設定（`loadData()`）
> - 註冊 CodeMirror extension、markdown processor
>
> **`onLayoutReady`**
> `app.workspace.onLayoutReady(callback)` 會等到 **workspace 完全就緒**（所有 leaf、file index 都載入完成）才執行 callback。
>
> 適合做：
> - 讀取目前開啟的檔案或 active leaf
> - 操作 workspace leaf（開視窗、注入 view）
> - 依賴 `app.vault.getFiles()` 或 metadata cache 的初始化邏輯
>
> 典型寫法：
> ```ts
> async onload() {
>   await this.loadSettings();
>   this.addCommand({ id: 'my-cmd', name: 'Do something', callback: () => {} });
>   this.addSettingTab(new MySettingTab(this.app, this));
>
>   this.app.workspace.onLayoutReady(() => {
>     this.initView();
>     this.scanActiveFile();
>   });
> }
> ```
>
> | 情境 | 用哪個 |
> |------|--------|
> | 註冊 command / event / setting | `onload` |
> | 操作 workspace leaf / view | `onLayoutReady` |
> | 讀取 active file、vault file list | `onLayoutReady` |
> | 需要 metadata cache 初始化完成 | `onLayoutReady` |
>
> **關鍵原則**：任何「假設 workspace 存在某個狀態」的操作，都放進 `onLayoutReady`，其餘放 `onload`。

### After [CLI 實測]（有 bu-ketao，~750 字）

> **`onload` vs `onLayoutReady`**
>
> **`onload`**
> Plugin 被載入時立即執行，此時 Obsidian UI **尚未完全渲染**。
>
> 適合：
> - 註冊 commands、settings、event listeners
> - 初始化資料結構、載入設定
> - 加掛 `addRibbonIcon`、`addStatusBarItem`
>
> **`onLayoutReady(callback)`**
> 在 `onload` 內呼叫，等 workspace layout 完全建立後才執行 callback。冷啟動時等 vault 載入完成；已開啟狀態下幾乎立即觸發。
>
> 適合：
> - 讀取目前開啟的 leaves / editors
> - 操作 `app.workspace.getActiveViewOfType()`
> - 需要存取現有 pane/tab 的任何初始化邏輯
>
> 典型用法：
> ```ts
> async onload() {
>   this.addCommand({ id: 'my-cmd', name: 'Do thing', callback: () => {} });
>   this.registerEvent(this.app.vault.on('create', this.handleCreate));
>
>   this.app.workspace.onLayoutReady(() => {
>     const leaf = this.app.workspace.getActiveLeaf();
>     // 安全操作 leaf
>   });
> }
> ```
>
> | | `onload` | `onLayoutReady` callback |
> |---|---|---|
> | 執行時機 | Plugin 掛載時立即 | Workspace layout 就緒後 |
> | Workspace 可用？ | 不保證 | 保證 |
> | 冷啟動延遲 | 無 | 有（等 vault index） |
>
> **原則**：凡是要碰 `app.workspace` 的現有狀態，進 `onLayoutReady`；其餘註冊類工作在 `onload` 頂層做。

**壓縮率：~17%**（兩版本結構相近，bu-ketao 版精簡了表格措辭，省略了部分場景描述）

---

## 情境 2：TypeScript build vs IDE 報錯不一致

**問題**：TypeScript 專案 build 時出現 'Type X is not assignable to type Y'，但 VS Code IDE 完全沒報錯，為什麼？

### Before [CLI 實測]（無 bu-ketao，~1,050 字）

> 這是個經典的「編譯器版本不一致」問題，根本原因有幾個：
>
> **1. TypeScript 版本不同**
> VS Code 預設使用**內建的 TypeScript**，而 `build` 指令使用**專案的 TypeScript**（`node_modules/.bin/tsc`）。
>
> 確認方式：
> ```bash
> ./node_modules/.bin/tsc --version
> # VS Code 命令面板：TypeScript: Select TypeScript Version → 查看目前版本
> ```
> 修正：命令面板執行 `TypeScript: Select TypeScript Version`，選 **Use Workspace Version**。
>
> **2. `tsconfig.json` 沒被 VS Code 正確載入**
> VS Code 的 TypeScript Language Server 可能讀的是**不同的 `tsconfig`**（例如根目錄的，而 build 用的是 `tsconfig.build.json`）。
> 確認方式：開啟有問題的檔案，在 VS Code 狀態列右下角確認載入的 config 是哪個。
>
> **3. `strict` 或其他 compiler options 不同**
> ```json
> // tsconfig.json（IDE 讀這個，較寬鬆）
> { "compilerOptions": {} }
>
> // tsconfig.build.json（build 用這個，較嚴格）
> { "compilerOptions": { "strict": true } }
> ```
>
> **4. VS Code 的 TypeScript Cache 過期**
> 命令面板執行 `TypeScript: Restart TS Server`。
>
> **快速診斷：**
> ```bash
> npx tsc --project tsconfig.json --noEmit
> npx tsc --project tsconfig.build.json --noEmit
> ```
> 比較兩者輸出，差異所在就是根因。

### After [CLI 實測]（有 bu-ketao，~900 字）

> 這是個經典的 **tsconfig 不一致**問題。
>
> VS Code 的 TypeScript language server 用的 tsconfig 和你跑 `tsc` / build tool 用的**不是同一份**。
>
> **具體排查點：**
>
> **1. VS Code 用了不同的 tsconfig**
> VS Code 預設找最近的 `tsconfig.json`，但 build 可能用的是 `tsconfig.build.json` 或 `tsconfig.prod.json`。
> 確認方式：看 `package.json` 的 build script 指定了哪個：
> ```json
> "build": "tsc -p tsconfig.build.json"
> ```
>
> **2. `strict` 或型別檢查選項不同**
>
> | 選項 | IDE tsconfig | build tsconfig |
> |---|---|---|
> | `strict` | false | true |
> | `strictNullChecks` | false | true |
> | `noImplicitAny` | false | true |
>
> **3. TypeScript 版本不同**
> VS Code 可能用 workspace 內的 tsc，也可能用內建版本。
> 確認：`Cmd+Shift+P` → `TypeScript: Select TypeScript Version`
>
> **4. `paths` / `baseUrl` 解析不同**
> Build tool（webpack、esbuild、vite）可能有自己的 alias 解析，讓 VS Code 認得但 tsc 不認。
>
> **5. `skipLibCheck` 差異**
> `tsconfig.json` 有 `"skipLibCheck": true` 但 build 沒有，第三方型別被 build 時檢查到。
>
> **快速驗證：**
> ```bash
> npx tsc -p tsconfig.json --noEmit
> npx tsc -p tsconfig.build.json --noEmit
> ```
> 錯誤只出現在其中一個 → tsconfig 設定不同就是根因。

**壓縮率：~14%**（兩版結構接近；bu-ketao 版多了 `paths`/`skipLibCheck` 兩個排查點，資訊量反而略多）

---

## 情境 3：Git rebase 衝突處理

**問題**：git rebase main 之後出現一堆 conflict，每個 commit 都要手動解，有沒有比較聰明的處理策略？

### Before（原始，~2,800 字）

> 好的，我來為你詳細說明 git rebase 衝突的處理策略。
>
> 當你執行 `git rebase main` 後出現大量衝突，這通常表示你的分支與 main 分支有較多的改動交集。首先，先確認衝突的根本原因。其次，考慮中止並改用 merge 策略。再者，使用互動式 rebase 重新組織 commit。另外，使用自動衝突解決策略。此外，分批 rebase。同時，使用外部工具。最後，檢查是否真的需要 rebase。
>
> 建議優先順序：第一步用 `git log --oneline` 看 commit 數量。第二步如果衝突少就手解。第三步已在 rebase 中段可用 `git rebase --skip`。
>
> 快速逃脫方案：`git rebase --abort` 回到 rebase 前...
>
> 希望這些策略對你有幫助！如果情況特別複雜，歡迎再詳述具體狀況。

### After（不客套 full，~800 字）

> 先確認：rebase 中途停了幾次？conflict 在哪些檔案？
>
> **方案 1：用 merge 替代（最快）**
> ```bash
> git rebase --abort
> git merge main
> ```
> 衝突集中一處解，比逐 commit 手解快。
>
> **方案 2：批量自動解（衝突模式重複時）**
> ```bash
> git rebase -X ours main   # 優先你的版本
> git rebase -X theirs main # 優先 main 版本
> ```
>
> **方案 3：重新整理分支（根本方案）**
> ```bash
> git reset --soft main     # 合併所有改動
> ```
>
> 衝突多且複雜 → merge。衝突集中少數檔案 → `-X ours/theirs`。提交太碎 → reset --soft 重整。

**壓縮率：~71%**

---

## 情境 4：Docker 記憶體洩漏排查

**問題**：Docker container 越跑越吃記憶體，本地開發沒問題，部署到 K8s 後被 OOMKilled，怎麼排查？

### Before（原始，~2,200 字）

> 這個問題通常是記憶體洩漏或環境差異造成的。以下是排查步驟：
>
> 首先，確認是真的洩漏還是正常的記憶體使用。用 `docker stats` 監控 RSS 趨勢，如果持續上升直到 OOMKilled，代表有洩漏。
>
> 其次，對比本地和 K8s 的環境差異。本地開發時運行量、並發數是否遠低於生產？K8s 可能有更多 Pod 同時跑。檢查環境變數設定（如 JVM heap size、Node.js memory limit、Python GC 策略）。需要注意的是，資料庫連線池設定也很重要。
>
> 再者，應用層排查。如果是 JVM 應用用 JProfiler 監控；如果是 Node.js 用 clinic.js 做 heap snapshot；如果是 Python 用 tracemalloc。檢查無限增長的快取。
>
> 另外，基礎設施層排查。K8s 的 requests/limits 設定是否太小？檢查 sidecar 是否吃記憶體。
>
> 最後，實際修復方向：設定合理的記憶體 limits、啟用監控告警、考慮用 alpine 基礎映像、檢查日誌輪轉。

### After（不客套 full，~900 字）

> **本地 vs K8s 記憶體差異三個原因：**
>
> 1. **資源限制不同**：本地沒 cgroup 約束，K8s 的 limit 會讓 app 看到虛假的可用記憶體。檢查 `kubectl describe pod` 的 requests/limits。
>
> 2. **洩漏門檻**：本地短時間跑，K8s 24h 連續，緩慢洩漏會累積。用 pprof（Go）/ memory_profiler（Python）/ clinic.js（Node）在 K8s 跑一晚對比 dump。
>
> 3. **環境差異**：併發量、快取配置、DNS 查詢頻率、連線池設定、sidecar 吃記憶體。
>
> **排查流程：**
> - `kubectl logs <pod> --previous` 看 OOMKilled 前的錯誤
> - 調高 limit 30%，觀察是漸進洩漏還是瞬間爆炸
> - Prometheus/Grafana 畫記憶體曲線，對應日誌找觸發點

**壓縮率：~59%**

---

## 情境 5：CSS flexbox vs grid 選擇

**問題**：CSS flexbox 和 grid 到底什麼時候該用哪個？

### Before（原始，~1,800 字）

> 簡單來說：flexbox 處理一維布局，grid 處理二維布局。
>
> 什麼時候用 Flexbox：導航列、頂部工具欄（水平排列）、按鈕組、表單欄位（單行或單列排列）、卡片內部的內容對齊、你只關心沿著一個軸的排列順序、需要 flex-wrap 自動換行的場景。
>
> 什麼時候用 Grid：整個頁面布局（header、sidebar、main content、footer）、儀表板、相簿（多行多列的規則排列）、複雜表單（多列多行）、你需要同時控制行和列的大小和位置。
>
> 實際判斷方法：問自己「我在處理一條線上的內容排列嗎？」用 Flexbox。「我在處理網格狀的二維佈局嗎？」用 Grid。
>
> 現代實踐：通常是嵌套組合。頂層 Grid（頁面架構），次層 Flexbox（各區塊內部排列）。簡單情況下 Flexbox 也能撐起二維布局（用 flex-wrap），但代碼會很亂。Grid 樣式碼更清晰，但學習曲線陡一點。

### After（不客套 full，~500 字）

> **Flexbox = 一維排列，Grid = 二維網格**
>
> 用 flexbox：導航列、按鈕群、卡片內容排版、動態個數項目 responsive 拆行。
>
> 用 grid：頁面整體佈局、固定網格（相片牆 3x3）、項目需要明確行列位置。
>
> **懶人法則**：能用 flexbox 搞定就不用 grid。Grid 是你需要「某元素在右上角，另一個在左下」才上場。

**壓縮率：~72%**

---

## 情境 6：Python GIL 解釋

**問題**：Python 的 GIL 是什麼？對多執行緒程式有什麼影響？

### Before（原始，~2,400 字）

> GIL（Global Interpreter Lock，全域直譯器鎖）是 CPython 為了簡化記憶體管理而實現的機制。它確保在任何時刻，只有一個執行緒能執行 Python 位元組碼。
>
> 簡單說：即使你有 4 核 CPU，CPython 的多執行緒程式也只能利用 1 核。
>
> 為什麼要有 GIL：CPython 使用引用計數做垃圾回收。每次變數賦值、銷毀都要更新計數器，計數器是共享的。加鎖保護計數器比實現 lock-free 的複雜並行演算法簡單得多。代價就是無法真正的並行執行。
>
> 對多執行緒程式的影響：首先，CPU 密集的任務會被拖慢。其次，I/O 密集的任務可以加速，因為執行緒在等待 I/O 時會釋放 GIL。
>
> 解決方案：multiprocessing 用獨立程序規避 GIL、async/await 單執行緒事件迴圈更輕量、C extension 用 NumPy 等在關鍵操作釋放 GIL、PyPy/Jython 使用其他 Python 實現。

### After（不客套 full，~550 字）

> **GIL = Global Interpreter Lock**
>
> Python 解釋器限制同一時刻只有一個 thread 執行 bytecode。多執行緒不能並行，只能輪流（時間分片）。
>
> **影響：**
> - CPU-bound 多執行緒無效（反而因 context switch 變慢）
> - I/O-bound OK（網路/磁碟阻塞時讓出 GIL）
> - 多核心優勢用不上
>
> **破解：**
> - I/O 用 asyncio 或 threading（會 yield GIL）
> - CPU 密集用 multiprocessing（獨立 process，各有一份 GIL）
> - 或改用 C extension / PyPy

**壓縮率：~77%**

---

## 情境 7：OAuth 2.0 Authorization Code Flow

**問題**：OAuth 2.0 的 Authorization Code Flow 是怎麼運作的？

### Before [CLI 實測]（無 bu-ketao，~1,300 字）

> 這是最常見、也最安全的 OAuth 2.0 流程，適用於有後端伺服器的應用程式。
>
> **角色定義：**
>
> | 角色 | 說明 |
> |------|------|
> | **Resource Owner** | 使用者本人 |
> | **Client** | 你的應用程式（前端 + 後端） |
> | **Authorization Server** | 負責驗證身份、發 token（如 Google、GitHub） |
> | **Resource Server** | 存放使用者資料的 API |
>
> **流程（ASCII 時序圖）：**
> ```
> User        Client          Auth Server       Resource Server
>  |             |                 |                   |
>  |--點擊登入-->|                 |                   |
>  |             |---302 redirect->|                   |
>  |             |  (response_type=code, client_id,    |
>  |             |   redirect_uri, scope, state)       |
>  |<---------登入頁面-------------|                   |
>  |---輸入帳密、同意授權---------->|                   |
>  |             |<--redirect back-|                   |
>  |             |  (?code=AUTH_CODE&state=...)        |
>  |             |---POST /token-->|                   |
>  |             |  (code, client_id,                  |
>  |             |   client_secret, redirect_uri)      |
>  |             |<--access_token--|                   |
>  |             |    refresh_token                    |
>  |             |---Bearer token----------------->    |
>  |             |<--使用者資料--------------------|   |
> ```
>
> **關鍵安全設計：**
> - `code` 透過瀏覽器 URL 傳遞，有外洩風險；`access_token` 的交換發生在**後端 server-to-server**，帶上 `client_secret`，不經過瀏覽器
> - `state` 參數：防止 CSRF 攻擊，Client 自行產生隨機值，callback 時驗證是否一致
> - **PKCE**：給無法安全保存 `client_secret` 的場景（SPA、行動 App），以 `code_verifier` + `code_challenge` 取代 `client_secret`
>
> **Token 種類：**
>
> | Token | 用途 | 壽命 |
> |-------|------|------|
> | `access_token` | 存取 Resource Server | 短（幾分鐘～1小時） |
> | `refresh_token` | 換新的 `access_token` | 長（數天～數月） |

### After [CLI 實測]（有 bu-ketao，~1,400 字）

> **角色：** Resource Owner（使用者）、Client（你的 App）、Authorization Server（Google/GitHub）、Resource Server（API）
>
> **流程：**
>
> 1. **User 點擊登入** → Client 將 User redirect 到 Authorization Server
> ```
> GET /authorize?
>   response_type=code
>   &client_id=CLIENT_ID
>   &redirect_uri=https://yourapp.com/callback
>   &scope=read:profile
>   &state=RANDOM_STATE
> ```
>
> 2. **User 登入並同意授權** → Authorization Server redirect 回 Client
> ```
> GET https://yourapp.com/callback?code=AUTH_CODE&state=RANDOM_STATE
> ```
>
> 3. **Client 用 `code` 換 token**（後端對後端，不經過瀏覽器）
> ```
> POST /token
> client_id=...&client_secret=...&code=AUTH_CODE&grant_type=authorization_code
> ```
>
> 4. **Authorization Server 回傳 token**
> ```json
> { "access_token": "...", "refresh_token": "...", "expires_in": 3600 }
> ```
>
> 5. **Client 帶 `access_token` 呼叫 Resource Server**
> ```
> GET /api/profile
> Authorization: Bearer ACCESS_TOKEN
> ```
>
> **關鍵設計：**
>
> | 機制 | 目的 |
> |------|------|
> | `state` 參數 | 防 CSRF，callback 時驗證是否一致 |
> | `code` 短效一次性 | 即使被截，無法重用 |
> | 用 secret 換 token 在後端做 | `client_secret` 不暴露給瀏覽器 |
> | `refresh_token` | `access_token` 過期後靜默換新，不需重新授權 |
>
> **與其他 Flow 比較：**
> - **Implicit Flow**（已棄用）：直接回傳 `access_token` 到前端，不安全
> - **PKCE**：Authorization Code Flow 延伸，給沒有後端的 SPA/行動 App 用，以 `code_verifier/challenge` 取代 `client_secret`

**壓縮率：-8%**（After 反而比 Before 更長！Before 用 ASCII 時序圖精簡了流程；After 補了完整 request/response 格式，資訊量更多）

---

## 情境 8：React 18 useEffect 雙重執行

**問題**：React 18 的 useEffect 為什麼會在開發模式下跑兩次？

### Before（原始，~1,800 字）

> 在 React 18，開發模式下使用 React.StrictMode 時 useEffect 會執行兩次，這是 React 團隊故意設計的行為。React 18 引入了 Strict Mode 的增強版，它會故意執行副作用兩次，藉此幫你發現那些依賴於副作用只執行一次這個假設的 bug。在開發模式下你會看到 Effect ran、Cleanup ran、Effect ran。第一次執行後立刻執行清理函式，然後再執行一次，這樣設計是為了驗證你的清理函式是否正確。生產環境不會這樣：打包並部署到生產環境時 Strict Mode 的雙重執行不會發生。最好的做法是寫出可以安全執行多次的 effect，確保 effect 和它的清理函式是冪等的。如果你不想看到這個行為，可以移除 React.StrictMode，但這樣就失去了診斷工具的好處。

### After（不客套 full，~250 字）

> React 18 開發模式啟用 Strict Mode，會故意執行兩次 useEffect 的清理函數和副作用，檢測是否有幽靈訂閱或資源洩漏。生產模式只跑一次。
>
> 目的：抓出開發階段的 bug（比如 fetch 沒清理、timer 沒 clearInterval）。

**壓縮率：~79%（token 計算：508 → 106，省 402 tokens）**

---

## 情境 9：MongoDB vs PostgreSQL 選擇

**問題**：MongoDB 和 PostgreSQL 怎麼選？什麼場景用哪個比較好？

### Before（原始，~2,000 字）

> MongoDB 和 PostgreSQL 是完全不同類型的資料庫，選擇哪個主要取決於你的應用特性。MongoDB 是 NoSQL 文檔型資料庫，適用場景：數據結構不固定或經常變化、快速原型開發、大量非結構化數據、水平擴展。優點：開發速度快 schema 靈活、查詢 JSON 文檔方便、分片成熟。缺點：缺少強制數據完整性、JOIN 效率低、事務支持較晚。PostgreSQL 是關聯式資料庫，適用場景：數據結構清晰穩定、複雜查詢和報表、數據完整性至關重要、強一致性。優點：ACID 事務、外鍵約束、複雜查詢效率高。缺點：schema 變更麻煩、水平擴展難。我的建議：如果你無法決定，PostgreSQL 是更安全的默認選擇。很多大公司使用混合策略。

### After（不客套 full，~300 字）

> **PostgreSQL**：結構化資料、ACID 事務、複雜查詢、強關聯性。用在電商訂單、金融帳戶、用戶系統。
>
> **MongoDB**：非結構化、文件導向、快速寫入、高並發讀。用在內容管理、日誌分析、IoT 時序數據。
>
> 選 PostgreSQL 當預設，除非需要水平擴展或文件格式差異大。

**壓縮率：~71%（token 計算：510 → 147，省 363 tokens）**

---

## 情境 10：Nginx WebSocket reverse proxy

**問題**：Nginx 做 reverse proxy 時，怎麼設定 WebSocket 支援？

### Before [CLI 實測]（無 bu-ketao，~1,100 字）

> Nginx reverse proxy 預設不會轉發 WebSocket 的 `Upgrade` header，需要手動加上。
>
> **最小設定：**
> ```nginx
> location /ws/ {
>     proxy_pass http://backend:3000;
>     proxy_http_version 1.1;
>     proxy_set_header Upgrade $http_upgrade;
>     proxy_set_header Connection "upgrade";
>     proxy_set_header Host $host;
>     proxy_cache_bypass $http_upgrade;
> }
> ```
>
> | 設定 | 原因 |
> |------|------|
> | `proxy_http_version 1.1` | WebSocket 需要 HTTP/1.1，預設是 1.0 |
> | `Upgrade $http_upgrade` | 轉發 client 的 `Upgrade: websocket` header |
> | `Connection "upgrade"` | 告知 backend 這是升級連線，不能用變數（有 bug） |
>
> **若整個 server block 都需要 WebSocket**（HTTP + WS 共用 `location`）：
> ```nginx
> http {
>     map $http_upgrade $connection_upgrade {
>         default upgrade;
>         ''      close;
>     }
>     server {
>         location / {
>             proxy_pass http://backend:3000;
>             proxy_http_version 1.1;
>             proxy_set_header Upgrade $http_upgrade;
>             proxy_set_header Connection $connection_upgrade;
>             proxy_set_header Host $host;
>         }
>     }
> }
> ```
>
> **常見問題：**
> - 連線頻繁斷線 → 調長 `proxy_read_timeout 3600s; proxy_send_timeout 3600s;`
> - Load balancer 後面 session 失效 → 加 `ip_hash` 或 `sticky`

### After [CLI 實測]（有 bu-ketao，~600 字）

> Nginx 預設不會轉發 WebSocket 的 `Upgrade` header，需要手動加上：
>
> ```nginx
> location /ws/ {
>     proxy_pass http://backend;
>
>     proxy_http_version 1.1;
>     proxy_set_header Upgrade $http_upgrade;
>     proxy_set_header Connection "upgrade";
>
>     # 可選但建議加
>     proxy_set_header Host $host;
>     proxy_set_header X-Real-IP $remote_addr;
>     proxy_read_timeout 3600s;
> }
> ```
>
> | 設定 | 原因 |
> |------|------|
> | `proxy_http_version 1.1` | WebSocket 需要 HTTP/1.1，預設是 1.0 |
> | `Upgrade $http_upgrade` | 轉發升級協議請求 |
> | `Connection "upgrade"` | 告知 backend 保持連線 |
>
> **注意：** `Connection "upgrade"` 不能寫 `$http_connection`，因為 Nginx 的 hop-by-hop header 處理會把它清掉，直接寫字串才能正確傳遞。
>
> 後端多節點時加 `ip_hash` 避免 session 飄移：
> ```nginx
> upstream backend {
>     ip_hash;
>     server 127.0.0.1:3001;
>     server 127.0.0.1:3002;
> }
> ```

**壓縮率：~45%**（After 去掉了 `map` 模式與 `proxy_cache_bypass`，精簡為核心三行 + `ip_hash` 說明）

---

## 情境 11：催款郵件（商業寫作）

**問題**：幫我寫一封催款郵件，客戶已經逾期 45 天沒付款，金額 38 萬，之前口頭催過兩次都沒下文。

### Before [CLI 實測]（無 bu-ketao，~950 字）

> 以下是一封語氣正式、保有施壓力道但不失禮的催款信：
>
> **主旨：【正式通知】應付款項逾期 45 天，請於期限內完成匯款**
>
> 您好，
>
> 本公司與　貴公司長期合作，一向秉持互信原則。然本次款項至今已逾期 45 天，金額新台幣 **380,000 元**，本公司業務人員亦曾兩度以電話口頭知會，迄今尚未收到任何回覆或付款安排。
>
> 為此，本公司正式發函通知，請 貴公司於收信後 **7 個工作天內**（即 **2026 年 4 月 29 日（二）前**）完成全額匯款，或主動聯繫本公司說明付款時程。
>
> **匯款資訊如下：**
>
> | 項目 | 內容 |
> |------|------|
> | 戶名 | （請填入） |
> | 銀行／分行 | （請填入） |
> | 帳號 | （請填入） |
> | 金額 | NT$ 380,000 |
>
> 若款項已於近日完成匯出，煩請回覆此信並附上匯款水單，以利核對。
>
> **若於上述期限前仍未收到款項，亦未有任何說明，本公司將依合約條款保留法律追訴之權利，並保留就逾期利息及相關費用求償之權利。**
>
> （署名）／（職稱）／（公司名稱）／（聯絡電話）／（日期）
>
> ---
> **使用建議：**
> - 7 天截止日已填入（4/29），可依實際需求調整
> - 若想加重壓力，可加：「如有任何付款困難，歡迎於 2026/04/22 前主動聯繫協商，否則本公司將不再保留協商空間。」
> - 建議以**掛號信或電子郵件+已讀回執**寄出，留存送達紀錄

### After [CLI 實測]（有 bu-ketao，~500 字）

> **主旨：** 【催款通知】發票款項逾期 45 天，請儘速處理
>
> 您好，
>
> 貴公司應付款項已逾期 45 天，迄今尚未收到付款，特此正式通知。
>
> **逾期款項明細：**
> - 金額：新台幣 380,000 元
> - 逾期天數：45 天
> - 先前聯繫：已口頭催款兩次，未獲回應
>
> 請於 **[日期，建議 5–7 個工作天內]** 前完成匯款，匯款資訊如下：
>
> > 戶名：[公司名稱]  
> > 銀行：[銀行名稱]  
> > 帳號：[帳號]
>
> 若款項已匯出，請回信告知匯款日期與末 5 碼，以利對帳。
>
> 如未於期限內收到款項或有效回覆，本公司將保留採取必要法律途徑之權利。
>
> [姓名] / [職稱] / [公司] / [聯絡方式]
>
> ---
> **調整建議：**
> - 有簽約 → 加「依據 [合約編號] 第 X 條約定付款期限」
> - 金額若含稅 → 標明含稅/未稅
> - 還款期限給越短越好（5 天），展示認真程度

**壓縮率：~47%**（After 去掉前言鋪陳、匯款表格改為純文字，信件正文更精煉）

---

## 情境 12：p-value 解釋（學術/研究）

**問題**：什麼是 p-value？為什麼 p < 0.05 不代表結果一定有意義？

### Before（原始，~1,400 字）

> 這是一個非常好的問題，也是統計學中最容易被誤解的概念之一。讓我來為您詳細解釋。
>
> 首先，我們需要了解 p-value 的正式定義。P-value，也就是 p 值，是指在虛無假設（null hypothesis）為真的前提下，觀察到當前數據或更極端數據的機率。簡單來說，p-value 衡量的是「如果真的沒有效果，我們看到這樣結果的可能性有多大」。
>
> 舉一個具體的例子來說明：假設你在測試一種新藥是否比安慰劑有效。虛無假設是「新藥和安慰劑沒有差別」。如果你得到 p = 0.03，這表示如果新藥真的沒有效果，你有 3% 的機率會觀察到這樣或更極端的差異。需要注意的是，這並不是說「新藥有 97% 的機率有效」，這是一個非常常見的錯誤解讀。
>
> 其次，關於 p < 0.05 這個門檻。0.05 這個數字是由統計學家 Ronald Fisher 在 1920 年代提出的，最初只是作為一個方便的參考值。然而，隨著時間的推移，它逐漸被學術界當作了一個硬性的標準。事實上，這個門檻的選擇在很大程度上是任意的，0.06 和 0.04 之間並沒有本質上的統計學差異。
>
> 再者，p < 0.05 不代表結果一定有意義，原因有以下幾點。第一，統計顯著性不等於實務顯著性。一個研究可能發現某藥物降低血壓 0.5 mmHg，p = 0.01，統計上顯著，但臨床上毫無意義。第二，多重比較問題。如果你同時檢驗 20 個假設，即使所有假設都是假的，純粹靠運氣也有大約 64% 的機率至少得到一個 p < 0.05 的結果。第三，樣本量的影響。足夠大的樣本量可以讓任何微小的差異都變得「統計顯著」。第四，p-hacking 問題。研究者可能有意或無意地通過調整分析方式、選擇性報告等手段來獲得 p < 0.05 的結果。
>
> 最後，現代統計學的趨勢是不再依賴單一的 p-value 門檻，而是綜合考慮效果量、信賴區間、以及研究設計的整體品質。美國統計協會（ASA）在 2016 年還專門發表了一份關於 p-value 的聲明，強調 p-value 不應該被用作判斷科學假設是否成立的唯一標準。
>
> 希望這個解釋能幫助您更好地理解 p-value 的含義和限制！如果您對假設檢定的其他方面有疑問，歡迎繼續提問。

### After（不客套 full，~450 字）

> **P-value = 虛無假設為真時，觀察到當前（或更極端）數據的機率。**
>
> 不是「效果為真的機率」，不是「結果可重現的機率」。
>
> **p < 0.05 不等於有意義的四個原因：**
>
> - **統計顯著 ≠ 實務顯著**：降血壓 0.5 mmHg，p = 0.01，臨床上沒用
> - **多重比較**：同時測 20 個假設，全是假的也有 ~64% 機率撈到一個 p < 0.05
> - **大樣本膨脹**：n 夠大，任何微小差異都會「顯著」
> - **p-hacking**：選擇性報告、調整分析方式、事後挑子集
>
> **0.05 門檻本身是任意的**（Fisher 1920s 的便利值），0.04 和 0.06 無本質差異。ASA 2016 聲明已明確反對用 p-value 作唯一判斷標準。
>
> 更好的做法：報告 effect size + 信賴區間 + 研究設計品質，不只看一個數字。

**壓縮率：~65%（token 計算：1,094 → 386，省 708 tokens）**

---

## 情境 13：台北三天兩夜行程（日常生活）

**問題**：我朋友從香港來台北玩三天兩夜，幫我推薦行程，他喜歡吃東西和逛老街。

### Before（原始，~1,500 字）

> 好的！您的朋友從香港來台北，喜歡美食和老街文化，我來為您規劃一個充實又不會太趕的三天兩夜行程。以下是我精心安排的建議：
>
> **第一天：抵達 + 西門町/萬華探索**
>
> 首先，建議抵達後先到飯店放行李、稍作休息。接著，中午可以前往西門町享用午餐，這裡有非常多元的美食選擇。推薦阿宗麵線，這是一家非常有名的老店，他們的大腸麵線口感滑順、味道濃郁，是很多遊客必吃的經典小吃。另外也推薦西門町的鴨肉扁，他們的鵝肉切盤配上特製醬汁非常美味。
>
> 下午可以步行前往萬華龍山寺一帶，龍山寺是台北最古老的寺廟之一，建於 1738 年，具有非常豐富的歷史文化價值。寺廟的建築雕刻精美絕倫，值得細細欣賞。龍山寺旁邊的剝皮寮歷史街區也非常值得一逛，這條老街保留了清朝到日治時期的建築風貌，街上有許多展覽空間和歷史介紹，可以深入了解台北的歷史發展。
>
> 晚上推薦前往華西街觀光夜市和廣州街夜市，這兩個夜市緊鄰在一起。華西街是台灣第一條觀光夜市，有很多傳統小吃，推薦蚵仔煎、排骨酥湯、青蛙下蛋等。需要注意的是，夜市通常下午五六點才開始熱鬧，建議不要太早去。
>
> **第二天：大稻埕 + 北投**
>
> 早上建議前往大稻埕迪化街，這是台北最具歷史底蘊的老街之一。迪化街在清末就是繁華的商業街區，至今仍保留著許多巴洛克風格和閩南式建築。街上有許多南北貨老店、中藥行、布莊等。近年來也進駐了不少文創小店和特色咖啡廳，傳統與現代融合得恰到好處。推薦在這裡吃個早午餐，例如民樂旗魚米粉湯，或是慈聖宮前的小吃攤區，那裡有許多道地的台灣早餐選擇。
>
> 中午過後，搭捷運前往北投。北投是台北著名的溫泉區，即使不泡溫泉，北投溫泉博物館、地熱谷等景點也非常值得參觀。北投溫泉博物館是一棟日治時期的公共浴場建築，免費參觀，裡面展示了北投溫泉的歷史和文化。地熱谷則是一個天然的溫泉湧泉口，煙霧繚繞的景象非常壯觀。
>
> 晚上回到市區，推薦前往寧夏夜市享用晚餐。寧夏夜市規模適中、美食密集度高，是台北在地人也愛去的夜市。必吃的包括劉芋仔蛋黃芋餅、蚵仔煎、豬肝湯等。
>
> **第三天：九份老街 + 離開**
>
> 如果時間允許，第三天早上可以安排前往九份老街。從台北搭客運大約一個小時可以到達。九份是一個依山面海的小鎮，老街沿著山坡蜿蜒而上，兩旁是各種小吃店和手工藝品店。推薦品嚐芋圓、草仔粿、魚丸等。從九份的觀景台可以俯瞰整個基隆山和太平洋的壯麗景色。需要注意的是，假日的九份人潮非常多，建議早點出發。
>
> 中午回到台北，如果還有時間，可以到永康街逛逛，吃個鼎泰豐或永康牛肉麵作為旅行的完美結尾。
>
> 以上就是我為您朋友規劃的三天兩夜行程。當然，具體行程可以根據實際情況和個人喜好進行調整。如果需要更詳細的交通資訊或餐廳推薦，歡迎隨時告訴我！祝您的朋友在台北有一個美好的旅程！

### After（不客套 full，~500 字）

> **D1 萬華老城區**
> - 午：西門町 → 鴨肉扁、阿宗麵線
> - 午後：龍山寺 + 剝皮寮歷史街區（清代至日治建築）
> - 晚：華西街 / 廣州街夜市（蚵仔煎、排骨酥湯）
>
> **D2 大稻埕 + 北投**
> - 早：迪化街（南北貨老街 + 文創店混合區）→ 慈聖宮前小吃攤早餐
> - 午後：捷運到北投 → 溫泉博物館（免費）+ 地熱谷
> - 晚：寧夏夜市（劉芋仔蛋黃芋餅、豬肝湯）
>
> **D3 九份 + 永康街**
> - 早：客運到九份（~1hr）→ 老街吃芋圓、草仔粿，觀景台看基隆山
> - 午：回台北 → 永康街（鼎泰豐 or 永康牛肉麵）→ 離開
>
> 注意：九份假日人爆多，早上 9 點前出發。夜市 17:00 後才熱鬧。

**壓縮率：~75%（token 計算：1,633 → 402，省 1,231 tokens）**

---

## 情境 14：拒絕加班（職場溝通）

**問題**：主管臨時叫我週末加班，但我已經有私人安排了，該怎麼拒絕又不影響關係？

### Before（原始，~1,300 字）

> 這確實是職場中非常常見也非常棘手的情況。拒絕主管的加班要求需要在維護自身權益和保持良好的工作關係之間取得平衡。以下是我的一些建議：
>
> 首先，我們需要理解一個重要的前提：拒絕加班是你的合法權利。根據勞動基準法的規定，加班應該是在勞資雙方都同意的情況下才能進行的，所以你完全有權拒絕，不需要有罪惡感。
>
> 其次，關於如何具體地表達拒絕。我建議採取以下步驟：
>
> 第一步，及時回應。不要拖延回覆，這樣會讓主管認為你在考慮中，給他留下希望，最後再拒絕反而更尷尬。收到請求後盡快回覆。
>
> 第二步，表達感謝和理解。先肯定主管信任你、願意把重要任務交給你。例如：「謝謝主管想到我，我理解這個案子時間很趕。」這樣可以表現出你對工作的重視和對團隊的尊重。
>
> 第三步，誠實但不過度解釋。你不需要詳細說明你的私人安排是什麼。只需要簡單明確地表示「這個週末我已經有事先安排好的行程，沒辦法調整」就夠了。過度解釋反而會讓人覺得你在找藉口，或者給主管機會來說服你改變計畫。
>
> 第四步，提供替代方案。這是非常關鍵的一步，因為它展現了你的積極態度和解決問題的能力。你可以提出：「我可以週五晚上先把能做的部分做完」、「我週一一早就來處理」、或者「需要的話我可以幫忙看看還有誰可以支援」。
>
> 第五步，保持堅定但友善的語氣。如果主管繼續施壓，你可以溫和但堅定地重申你的立場。記住，一旦決定拒絕，就不要在態度上搖擺不定，因為這會讓主管覺得再推一下你就會答應。
>
> 最後，一些額外的注意事項。事後的態度也很重要，週一上班後主動關心一下專案進度，表現出你依然在意團隊和工作。另外，平時的工作表現才是根本，如果你平常表現好、效率高、配合度也不差，偶爾拒絕一次加班，合理的主管都能理解。
>
> 具體的回覆範例：「主管好，謝謝您想到我。這個週末我已經有之前安排好的行程，沒辦法來加班。不過我可以週五下班前先把 [X 部分] 做到一個段落，週一一進公司就接著處理，不會耽誤整體進度。您看這樣可以嗎？」
>
> 這樣的回覆既表達了你的立場，又展現了責任心。希望這些建議對您有幫助！如果您需要根據具體情況調整措辭，歡迎再告訴我。

### After（不客套 full，~350 字）

> **核心原則**：快回覆 + 不解釋私事細節 + 給替代方案。
>
> **直接範本：**
>
> 「主管好，這週末有先前排定的行程無法調開。我週五下班前先把 [X] 做到段落，週一早上接著處理。或者我幫看看誰可以支援？」
>
> **拒絕時避免：**
> - 拖延回覆（主管以為你在猶豫）
> - 過度解釋行程內容（像在求批准）
> - 語氣搖擺（對方會覺得再推就行）
>
> **加分動作**：週一主動問專案進度，讓主管知道你在意。
>
> 加班需勞資同意（勞基法），拒絕是權利，不需要罪惡感。平時表現好，偶爾拒絕一次合理主管都能接受。

**壓縮率：~75%（token 計算：1,138 → 284，省 854 tokens）**

---

## 總結

### 字數壓縮（CLI 雙向實測，2026-04-18）

> 標注 `†` 的情境為 CLI 雙向實測（Before = 無規則，After = bu-ketao），其餘為假設性對比。

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

### 實測觀察（2026-04-18，雙向 CLI 測試）

**核心發現：**

1. **原始文件的 Before 是最壞情況假設**：實際 `claude-sonnet-4-6` 無規則輸出已相當精簡，不帶「您好！讓我來幫你...」之類的臃腫開場
2. **CLI 實測壓縮率大幅低於假設值**（14%–47% vs 假設的 59%–87%）
3. **Q7（OAuth）After 比 Before 更長**：bu-ketao 不是硬性截短，而是把資訊組織得更完整；當 Before 已夠精簡時，After 反而更詳盡
4. **bu-ketao 仍有效的場景**：非技術類（催款信、職場溝通）壓縮效果更明顯（~45–75%），因模型在商業/生活情境仍會加入「語氣說明」與「使用建議」的篇幅
5. **假設性 Before 的壓縮率**（71%–87%）反映的是對話初期 prompt-naive 輸出 vs 規則最佳化輸出的差距，代表 bu-ketao 對舊版模型或無系統提示場景的效益

### 成本換算（CLI 實測 5 組，估算）

以 Claude Sonnet output 定價 $15/M tokens 估算：

| 組別 | Before tokens（估） | After tokens（估） | 省下 | 壓縮率 |
|------|--------------------|--------------------|------|--------|
| Q1 Obsidian | ~230 | ~190 | ~40 | 17% |
| Q2 TypeScript | ~270 | ~230 | ~40 | 15% |
| Q7 OAuth | ~330 | ~360 | -30 | -9% |
| Q10 Nginx | ~280 | ~155 | ~125 | 45% |
| Q11 催款 | ~245 | ~130 | ~115 | 47% |
| **5 組合計** | **~1,355** | **~1,065** | **~290** | **~21%** |
| 推算 14 組 | ~3,800 | ~3,000 | ~800 | ~21% |
| **成本差** | $0.057 | $0.045 | **$0.012** | |

> 注意：假設性 Before 情境（假設性臃腫輸出）的壓縮率更高（~69%），代表 bu-ketao 對「較舊模型」或「無調教 prompt」場景的成本節省效益遠大於此。
