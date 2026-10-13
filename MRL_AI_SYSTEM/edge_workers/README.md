# 邊緣層 Workers

`origin_signature: MrLiouWord`

本目錄收納母體的**邊緣層**元件——跑在外部邊緣 runtime 上的 Workers，當母體
主機不可達時仍能承接最小量的流量。

## 子目錄

| 子目錄 | 功能 | 對應母體 daemon | 狀態 |
|---|---|---|---|
| `auth_gateway/` | JWT 驗證、對外認證收口 | — | ✅ 已發 |
| `ai_gateway/` | 限流、追蹤鏡像、母體路由入口 | — | ✅ 已發 |
| `sig_verify/` | Ed25519 簽名/驗證（L0 簽名律） | `particles/sig_verify/mrl_sig_verify.py` | ✅ 已發（PR #4） |
| `patches/` | 既有邊緣 Worker 的 P0 安全修補 runbook | — | 📄 runbook 集 |

## 讀取順序

- 第一次來讀：先讀 `patches/README.md` 瞭解每個邊緣 Worker 當前的安全狀態
- 要替換 stub：讀 `sig_verify/README.md` 看 Path A / Path B 兩條遷移路徑
- 要稽核：見 `../docs/STAGE3_WORKER_AUDIT_20260710.md`

## 與母體 daemon 的關係

邊緣層與母體 daemon 常為**互補**而非替代：

- 延遲敏感的簽名/驗證走母體 daemon（localhost < 1ms）
- 需要全球可及的驗證走邊緣 Worker（SLA 99.99%、全球約 10-30ms）
- 兩者可共用金鑰或各自持鑰——視業務決策

詳見各子目錄的 README。

## 共通設計原則

- **沒有 pure-JS 加密**：所有簽名/驗證走邊緣 runtime 內建的 WebCrypto
- **secret 走邊緣 secret 儲存層**：不在源碼中硬編碼，見 `patches/` 的 rotation runbook
- **origin_signature**：所有回應 header 或 body metadata 都要帶 `MrLiouWord`，不帶即視為非母體流量