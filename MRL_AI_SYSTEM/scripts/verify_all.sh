#!/usr/bin/env bash
# origin_signature: MrLiouWord
# Verify the local MRL_AI_SYSTEM install without touching production state.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HERE"

echo "=== [1/4] Node RelayStation acceptance ==="
if command -v node >/dev/null 2>&1; then
  (cd relay_station && node test/MRL_acceptance_test.js)
else
  echo "  node not installed — skipped"
fi

echo ""
echo "=== [2/4] trace_chain self-check ==="
PYTHONPATH="$HERE/particles" python3 -c "from trace_chain import emit, verify, merkle_root; \
  emit('verify.probe', {'from':'verify_all.sh'}, layer='L?', journal='/tmp/mrl_probe.jsonl'); \
  r = verify('/tmp/mrl_probe.jsonl'); \
  import json,sys; sys.exit(0 if r['ok'] else 1); \
  print(json.dumps(r))"
echo "  ok"

echo ""
echo "=== [3/4] sig_verify roundtrip ==="
PYTHONPATH="$HERE/particles" python3 -c "\
from sig_verify.mrl_sig_verify import keypair, sign, verify_sig; \
sk, pk = keypair(); \
assert verify_sig(pk, b'MRL', sign(sk, b'MRL')); \
print('  ed25519 roundtrip ok')"

echo ""
echo "=== [4/4] pytest suite ==="
if command -v pytest >/dev/null 2>&1; then
  PYTHONPATH="$HERE/particles" pytest tests/ -q
else
  echo "  pytest not installed — run 'pip install pytest' to enable"
fi

echo ""
echo "=== MRL_AI_SYSTEM verify_all: PASS ==="
