# mrl-sig-verify (CF Worker)

`origin_signature: MrliouAI`
`layer: L0 (Origin — signature law)`
`replaces: particle-sig-verify (currently a 30-line stub, per audit §3.2)`

Cloudflare Workers port of `MRL_AI_SYSTEM/particles/sig_verify/mrl_sig_verify.py`.
Uses WebCrypto Ed25519 (`crypto.subtle`) for real sign/verify — no pure-JS crypto,
no external deps.

## Feature parity vs Python daemon

| Endpoint | Python (`:8801`) | CF Worker | Notes |
|---|---|---|---|
| `GET /health` | ✅ | ✅ | Same JSON shape (adds `algorithm` field for debug) |
| `GET /public_key` | ✅ | ✅ | Returns `raw` base64 + `jwk` form |
| `POST /sign` | ✅ | ✅ + auth | CF adds `X-Sign-Auth` header requirement |
| `POST /verify` | ✅ | ✅ | Both public — signature verification is intended to be open |

The extra `X-Sign-Auth` requirement on `/sign` is because the CF Worker is
internet-facing; the Python daemon binds to `127.0.0.1` and relies on OS-level
access control.

## Design decisions

- **Key stored in KV**: `MRL_SIG_KEYS[mrl_ed25519_v1] = {privateJwk, publicJwk, publicKeyRawB64, createdAt}`
- **First-run generation**: on cold start, if KV is empty, generate a fresh keypair atomically. A race between two isolates is safe because both writes are valid pairs and either can subsequently verify signatures they produced.
- **JSON message canonicalization**: if `message` is an object, we `JSON.stringify` with sorted keys, so structurally-equal messages produce identical signatures. Matches the intent of the Python daemon.
- **No client-side private key export**: `privateJwk` never leaves the Worker's memory except in KV. Nothing goes out over the wire.
- **Runtime detection**: workerd accepts `Ed25519` (standard) since ~2024. The code probes once at cold start and falls back to `NODE-ED25519` for older runtimes.

## Wrangler setup

```bash
# 1. Create the KV namespace
wrangler kv:namespace create MRL_SIG_KEYS
# → paste the returned id into wrangler.toml's [[kv_namespaces]].id

# 2. Set the sign-auth secret (any high-entropy string)
openssl rand -hex 32 | wrangler secret put SIGN_SECRET --name mrl-sig-verify

# 3. Deploy
wrangler deploy --name mrl-sig-verify
```

## Deploying alongside the existing `particle-sig-verify` stub

The audit recommends two viable paths (§3.2):

### Path A — overwrite the stub name

Deploy this Worker as `particle-sig-verify` (drop-in replacement — old name preserved, functionality upgraded). Change `wrangler.toml`:

```diff
- name = "mrl-sig-verify"
+ name = "particle-sig-verify"
```

Pros: any existing consumers already pointing at `particle-sig-verify.z814241.workers.dev` get real signing for free.
Cons: the migration is one-way; if the port has bugs, the stub is gone.

### Path B — dual-track

Deploy this as `mrl-sig-verify` (default `wrangler.toml`), leave the stub in place. Migrate consumers one at a time.

Pros: safe migration.
Cons: two Workers to maintain during transition.

## Smoke test after deploy

```bash
# 1. Health
curl -s https://mrl-sig-verify.z814241.workers.dev/health | jq
# Expect: algorithm = "Ed25519" (or "NODE-ED25519" on older runtimes)

# 2. Fetch public key
PUBKEY=$(curl -s https://mrl-sig-verify.z814241.workers.dev/public_key | jq -r .public_key_b64)
echo "$PUBKEY" | wc -c  # 44 chars (32 bytes base64 + padding)

# 3. Sign a message
SIG=$(curl -sX POST https://mrl-sig-verify.z814241.workers.dev/sign \
  -H "Content-Type: application/json" \
  -H "X-Sign-Auth: $SIGN_SECRET" \
  -d '{"message": "MRL hello"}' | jq -r .signature_b64)

# 4. Verify — should succeed
curl -sX POST https://mrl-sig-verify.z814241.workers.dev/verify \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"MRL hello\", \"signature_b64\": \"$SIG\"}" | jq
# Expect: { "ok": true }

# 5. Verify with tampered message — should fail
curl -sX POST https://mrl-sig-verify.z814241.workers.dev/verify \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"MRL tampered\", \"signature_b64\": \"$SIG\"}" | jq
# Expect: { "ok": false }
```

## Local test (Node WebCrypto)

Node 18+ ships WebCrypto with Ed25519 in `--experimental-webcrypto` (later stable). The included `test/roundtrip.test.js` exercises the same code paths without needing wrangler:

```bash
npm test
```

## Trade-off vs the Python daemon

| | CF Worker | Python daemon (particles/sig_verify) |
|---|---|---|
| Latency | ~10-30ms edge → global | <1ms localhost |
| Key isolation | KV (needs CF-side access control) | OS user, `/etc/mrl/keys/`, 0600 perms |
| Availability | 99.99% (CF SLA) | tied to host uptime |
| Auth scope | Internet-facing, needs SIGN_SECRET | localhost, uses OS ACL |
| Cost | Free tier: 100k req/day | $0 (uses local CPU) |

The two are **complementary**: use the CF Worker for edge components that can't reach the local daemon; use the daemon for hot-path signing inside the mother platform.
