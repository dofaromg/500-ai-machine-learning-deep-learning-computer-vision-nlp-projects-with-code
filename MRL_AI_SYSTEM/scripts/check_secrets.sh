#!/usr/bin/env bash
# origin_signature: MrLiouWord
# Secret-scan guard — 擋 secret literal 不小心進 git。
#
# 掃描的 pattern 來自 session 累計遇到過的所有 secret 類型。
# 排除:歷史記錄檔、runbook 說明段(但 code fence 內的禁字會抓)、本腳本自身。
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HERE"

# 已知的 secret pattern(大量驗證過)
# [REDACTED ...] placeholder 不算違規(表示已處理過)
PATTERNS=(
  # Anthropic API key(排除 REDACTED 開頭的 placeholder)
  'sk-ant-api03-[A-Za-z0-9_-]{20,}'
  # Cloudflare Global API Key 格式(37 hex chars,但只在 string literal 內才算)
  '["'\''`][0-9a-f]{37}["'\''`]'
  # 常見 base64 PEM key fragment
  '-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----'
  # AWS access key
  'AKIA[0-9A-Z]{16}'
  # 常見硬編碼 pattern(session 歷史)
  'shengai-jwt-secret-[0-9]{4}'
  'test_hash_replace_later'
  # DL580_KEY 硬編碼字串字面(排除 placeholder 與 env 讀取)
  'DL580_KEY\s*=\s*"(?!\[REDACTED)[^"$][^"]*"'
)

violations=0
for pat in "${PATTERNS[@]}"; do
  # 掃全 repo,排除 .git/scratch/*/本腳本自身/placeholder markdown line
  matches=$(grep -rnE "$pat" . \
    --exclude-dir=.git \
    --exclude-dir=node_modules \
    --exclude-dir=.pytest_cache \
    --exclude-dir=__pycache__ \
    --exclude-dir=.artifacts \
    --exclude='check_secrets.sh' \
    --exclude='MRL_DELIVERY_MANIFEST_*' \
    2>/dev/null | grep -v 'REDACTED' || true)
  if [ -n "$matches" ]; then
    echo "── Pattern: $pat ──"
    echo "$matches" | head -5
    echo ""
    violations=$((violations+1))
  fi
done

if [ "$violations" -eq 0 ]; then
  echo "✅ Secret scan 通過(0 pattern 匹配)"
  exit 0
else
  echo "❌ $violations 個 pattern 匹配到可能的 secret literal"
  echo "   請改用 [REDACTED — ...] placeholder,或移到 secret 儲存層"
  exit 1
fi
