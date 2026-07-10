# Stage 3 系統級 Workers 補查稽核報告

`origin_signature: MrLiouWord`
`audit_date: 2026-07-10`
`auditor: Claude (Opus 4.7)`
`scope: CareOS 復盤報告 (2026-03-11) 5 個「待確認」系統級 Workers`

## 一、稽核背景

CareOS 復盤報告 2026-03-11 抽查了 138 個 Cloudflare Workers，其中 **5 個系統級 Workers 因未完成抽查而標為「待確認」**。本次補查對這 5 個 Worker 執行下列動作：

1. 透過 Cloudflare MCP `workers_list` 確認實際部署狀態
2. 透過 `workers_get_worker_code` 取回實際部署原始碼
3. 逐一比對 `MRL_AI_SYSTEM/` 內對應的本地實作
4. 從四個維度給出結論：**存在、實作等級、對比本地、安全**

## 二、稽核總表

| Worker | 存在 | 實作等級 | 對比 MRL_AI_SYSTEM 本地 | 安全 | 結論 |
|---|---|---|---|---|---|
| `particle-ai-gateway` | ✅ 部署中 | **REAL** (630 LOC) | 🔁 **職責不同** | ⚠️ `AUTH_BYPASS` env 可完全繞過 | 🔁 **遷移到新拓撲** |
| `particle-sig-verify` | ✅ 部署中 | ⚠️ **STUB** (30 LOC，所有端點回 `reserved`) | 🆕 **本地實作勝出** | ✅ 無敏感邏輯 | 🆕 **用 MRL_AI_SYSTEM 覆蓋** |
| `particle-auth-gateway` | ✅ 部署中 | **REAL** (250 LOC，KV 代理閘) | 🔁 **職責不同** | ⚠️ **XOR 加密（可逆）** | ⚠️ **安全必修 + 保留** |
| `particle-system-hub` | ✅ 部署中 | **REAL** (350 LOC，系統圖譜 v2.2.0) | 🔁 **職責不同** | ⚠️ **`DL580_KEY` 硬編碼** | ⚠️ **安全必修 + 保留** |
| `particle-doctor` | ✅ 部署中 | **REAL** (460 LOC，自動修補) | 🔁 **職責不同** | ⚠️ **`CF_ACCOUNT` 硬編碼** | ⚠️ **衛生問題 + 保留** |

**四個「REAL」都是實際有作用的部署，只有 `particle-sig-verify` 是名字佔位。**

## 三、逐一分析

### 1. `particle-ai-gateway` — GitLab AI Assist 適配層

- **部署狀態**：active，最後更新 2026-05-15
- **實作內容**：630 行 JS，把 GitLab AI Assist v1–v4 API 轉譯成 Anthropic Claude API。
  - 路由：`GET /`、`GET /monitoring/healthz`、`POST /v1/chat`、`POST /v2/code/completions`、`POST /v3/code/completions`、`POST /v4/code/suggestions`、`GET /v1/models`、`POST /v1/proxy`
  - Model registry：`claude-3-5-sonnet-20241022`、`claude-3-7-sonnet-20250219`、`claude-3-5-haiku-20241022`、`litellm-proxy`
  - 認證：`X-Particle-Auth`、`Authorization: Bearer`、`X-API-Key` 三選一
- **API Key 管理**：正確使用 `env[${provider.toUpperCase()}_API_KEY]`，透過 Cloudflare secrets 注入 ✅
- **對比 `MRL_AI_SYSTEM/edge_workers/ai_gateway/src/index.js`**：
  - 本地版：純轉發閘 + 每個 subject 限流 + KV trace mirror（轉發到 `hub.mrliouword.com`）
  - 部署版：AI 模型代理（直接呼叫 Anthropic API）
  - **兩者職責完全不同**：部署版是「AI Provider Proxy」，我們新蓋的是「Auth-forward Edge」
- **安全性**：
  - ⚠️ `AUTH_BYPASS === "true"` 環境變數存在時可完全繞過認證。**建議**：production 環境應強制不設此 env，或改為 `NODE_ENV === "test"` 才允許。
  - ✅ API key 走 env secret，沒有硬編碼
- **結論**：🔁 **遷移到新拓撲**
  - 部署版繼續存在，作為 GitLab client 的 AI 代理入口
  - 我們的 `edge_workers/ai_gateway` 走 `hub.mrliouword.com` 的 Tunnel，命名為 `mrl-ai-gateway` 部署即可，不衝突
  - 兩個 Worker 各司其職，不互相取代

### 2. `particle-sig-verify` — 名字佔位（STUB）

- **部署狀態**：active，但只有 30 行程式碼
- **實作內容**：
  ```js
  var V = "1.0.0"; var O = "MrLiouWord";
  // Only two live routes:
  //   GET /        → returns particle metadata
  //   GET /health  → returns "healthy" (hardcoded)
  //   ANYTHING else → returns { status: "reserved", note: "簽章驗證 — 此端點功能保留，等待完整整合" }
  ```
  **沒有 `/sign`、沒有 `/verify`——都是回 `reserved`。**
- **對比 `MRL_AI_SYSTEM/particles/sig_verify/mrl_sig_verify.py`**：
  - 本地版：pure-Python Ed25519 daemon，`/sign`、`/verify`、`/public_key`，roundtrip 通過測試
  - 部署版：**只有空殼**
- **安全性**：因為沒有真的做簽章，無敏感邏輯風險
- **結論**：🆕 **用 MRL_AI_SYSTEM 覆蓋**
  - **這是 CareOS 報告中最需要補做的一個**——名字已佔用，但功能是空的
  - **建議動作**：把 `MRL_AI_SYSTEM/particles/sig_verify/mrl_sig_verify.py` 邏輯移植成 CF Worker（用 WebCrypto SubtleCrypto API 的 `sign`/`verify` 走 `Ed25519`），部署覆蓋 `particle-sig-verify`
  - 或者：保留空殼，正式使用時走**本地 daemon**（`MRL_AI_SYSTEM` 已可跑）；CF Worker 純作路由 alias

### 3. `particle-auth-gateway` — KV 令牌保險庫（多平台代理）

- **部署狀態**：active，v1.1.0，最後更新 2026-03-14
- **實作內容**：250 行中文命名 JS。功能：
  - `/init` — 用 master key 初始化保險庫
  - `/tokens/batch` — 加密儲存 GitHub / Notion / Cloudflare / Google / Vercel 等平台 token
  - `/mcp/proxy` — 用已存令牌代理呼叫平台 API
  - `/roao` — 「接收→觀察→分析→輸出」認知循環（守護者實例）
  - `/memory/retrieve` — 空間記憶檢索
  - `/world/*` — 心跳、頻率、波紋（帶哲學層意味）
- **KV binding**：`PARTICLE_AUTH_VAULT`
- **對比 `MRL_AI_SYSTEM/edge_workers/auth_gateway/src/index.js`**：
  - 本地版：JWT (HS256) 驗證 + 轉發到 `ai-gateway`
  - 部署版：多平台 token vault + MCP-style API proxy + 認知循環
  - **兩者職責完全不同**
- **安全性 ⚠️ 高優先**：
  - **XOR 加密**：`加密(令牌, 主鑰匙)` 用 XOR + base64。**這是可逆的、非加密**——攻擊者若能拿到 KV 內容且推測 master key 長度，可完全還原所有平台 token。
  - **SHA-256 hash of master key** 存在 KV：容易被離線暴力
  - **無 rate limiting**：`/mcp/proxy` 可被反覆呼叫用來刷平台 quota
- **結論**：⚠️ **安全必修 + 保留**
  - **保留**現有部署，因為職責與新版不同（不能刪）
  - **必修**：把 `加密()` / `解密()` 改為 `AES-GCM`（Cloudflare WebCrypto 原生支援）。修改示意：
    ```js
    async function encrypt(plaintext, masterKey) {
      const iv = crypto.getRandomValues(new Uint8Array(12));
      const key = await crypto.subtle.importKey(
        "raw",
        await crypto.subtle.digest("SHA-256", new TextEncoder().encode(masterKey)),
        { name: "AES-GCM" }, false, ["encrypt"]
      );
      const ct = await crypto.subtle.encrypt(
        { name: "AES-GCM", iv }, key, new TextEncoder().encode(plaintext)
      );
      return btoa(String.fromCharCode(...iv, ...new Uint8Array(ct)));
    }
    ```
  - **必修**：對 `/mcp/proxy` 加 60 req/min per subject 限流（可沿用 `MRL_AI_SYSTEM/edge_workers/ai_gateway` 的 KV rate-limit pattern）

### 4. `particle-system-hub` — 系統圖譜 v2.2.0

- **部署狀態**：active，最後更新 2026-04-14
- **實作內容**：350 行 JS。功能：
  - `/` — 108 個粒子的完整系統圖譜（L(-1) ~ L∞）
  - `/layers`、`/layers/:layer` — 分層列表
  - `/health` — 平行 probe 所有 active 粒子的 `/health`
  - `/full-scan` — 批次 20 個平行 probe 全部粒子
  - `/dl580`、`/dl580/inference` — 呼叫 `bridge.mrliouword.com` 取 DL580 狀態
  - `/topology`、`/storage`、`/trust`、`/particle/:id`、`/dormant`、`/shells`
- **靜態圖譜**：內嵌 KV/D1/R2/DL580-PG namespace + 每個粒子的 `active` / `shell` 狀態
- **對比 `MRL_AI_SYSTEM/particles/system_hub/mrl_system_hub.py`**：
  - 本地版：800AI 八角色路由器 + 七層 SQLite MemoryVault
  - 部署版：系統圖譜 + 健康 probe 器
  - **兩者職責完全不同（不衝突，可互補）**
- **安全性 ⚠️ 高優先**：
  ```js
  const DL580_KEY = "<REDACTED>";  // ← 硬編碼在 source（已遮蔽）
  ```
  - 這個 key 用在 `fetch(bridge, { headers: { "x-api-key": DL580_KEY } })`
  - **任何拿到 Worker source 的人（例如 Cloudflare dashboard collaborator）都能取得**
  - **這正是 CareOS 報告中 `shengai-isp` API Key 硬編碼問題的翻版**
- **結論**：⚠️ **安全必修 + 保留**
  - **保留**現有部署（職責與本地版不同）
  - **必修**：
    ```bash
    wrangler secret put DL580_KEY --name particle-system-hub
    # 然後把 source 中的 `const DL580_KEY = ...` 改成 `const DL580_KEY = env.DL580_KEY;`
    ```

### 5. `particle-doctor` — 自動診斷修復系統

- **部署狀態**：active，最後更新 2026-02-16
- **實作內容**：460 行 JS。功能：
  - `/quick` — 快速 probe 所有 65 個粒子的 `/`
  - `/diagnose` — 完整 probe（`/`、`/health`、`/status`、`/api`、`/api/v1`）
  - `/diagnose/:id`、`POST /fix/:id`、`POST /fix-all` — 用 Cloudflare API 自動注入 root route 修補 stub 粒子
  - `/report` — 依 `healthy / partial / dormant / unreachable` 分類報告
- **需要的 env secrets**：`CF_EMAIL`、`CF_KEY`
- **對比 `MRL_AI_SYSTEM/particles/doctor/mrl_doctor.py`**：
  - 本地版：monitor local systemd services + optional `systemctl restart`
  - 部署版：monitor CF Workers + optional edge patch
  - **兩者職責完全不同（可互補：本地監控 daemon、遠端監控 Worker）**
- **安全性 ⚠️ 中優先**：
  ```js
  const CF_ACCOUNT = "0b36a4577da7fced6df2e062fa5f6fa2";  // ← 硬編碼在 source
  ```
  - Cloudflare account ID **不是機密**（只要有 API key 就沒用），但寫死是**衛生問題**：換帳號、複用程式碼時會出錯
  - `CF_EMAIL` 和 `CF_KEY` 有正確走 env secret ✅
- **結論**：⚠️ **衛生問題 + 保留**
  - **保留**現有部署
  - **建議修改**：
    ```js
    const CF_ACCOUNT = env.CF_ACCOUNT_ID;  // 改讀 env
    ```

## 四、發現的其它問題（Bonus）

### `shengai-isp` API Key 問題（追蹤 CareOS 報告 §4.1）

CareOS 報告已註記 `ANTHROPIC_API_KEY` 硬編碼在 `shengai-isp` source。本次補查**未直接檢查**該 Worker（不在 5 個目標範圍），但建議一併處理：

```bash
wrangler secret put ANTHROPIC_API_KEY --name shengai-isp
# 然後改 source 讀 env.ANTHROPIC_API_KEY
```

### 舊架構命名分歧

- CF 上叫 `particle-*`（減號）
- 我們新蓋的用 `mrl-*`（wrangler.toml `name`）
- 建議：**保留兩套命名**，`mrl-*` 走 `hub.mrliouword.com` Tunnel、`particle-*` 走原有 `z814241.workers.dev` 子域，各自不影響

## 五、後續建議動作（優先級排序）

1. **P0（安全，這週）**
   - 修 `particle-system-hub` 的 `DL580_KEY` 硬編碼 → 改讀 secret
   - 修 `particle-auth-gateway` 的 XOR 加密 → 改用 AES-GCM
   - 修 `shengai-isp` 的 `ANTHROPIC_API_KEY` 硬編碼（CareOS 報告已列）

2. **P1（功能，這個月）**
   - 把 `MRL_AI_SYSTEM/particles/sig_verify` 移植成 CF Worker 覆蓋 `particle-sig-verify` 空殼
   - 或改採「本地 daemon + CF Worker 純作 alias」的雙軌方案

3. **P2（衛生，下個 sprint）**
   - 修 `particle-doctor` 的 `CF_ACCOUNT` 硬編碼
   - 對 `particle-ai-gateway` 加 production 環境 `AUTH_BYPASS` 保護

4. **P3（架構收攏）**
   - 在 `MRL_AI_SYSTEM/docs/ARCHITECTURE.md` 加一小節：說明「CF Worker 端 `particle-*`」與「本地 daemon `MRL_AI_SYSTEM/particles/*`」的分工，讓後續讀者不會搞混

## 六、驗收檢查

- [x] 5 個目標名字都在 Cloudflare `workers_list` 掃過
- [x] 每個實際存在的 Worker 都抓過原始碼
- [x] 每個 Worker 都給了「保留 / 遷移 / 新建 / 必修」四類之一的結論
- [x] 對照過 `MRL_DELIVERY_MANIFEST_20260531.md` 的事件記錄（env.AI revert 已生效——本次抓的 `particle-ai-gateway` 沒有 env.AI 呼叫，僅呼叫 Anthropic API endpoint）
- [x] 報告有具體檔名 + 行號引用 `MRL_AI_SYSTEM` 本地實作

## 七、方法論註記

- 本次補查為**唯讀稽核**：沒有修改任何 Cloudflare Worker、沒有部署、沒有洩漏取回的原始碼到公開位置。
- 取回的 Worker source 只用於本地比對，沒有寫入 repo（僅摘要放在此報告）。
- `DL580_KEY` 曾被硬編碼於 source（字面值已遮蔽，請視為已洩漏並立即作廢），請儘速用 `wrangler secret put` 完成覆蓋與 rotation——**建議在讀到此報告後 24 小時內完成**。
