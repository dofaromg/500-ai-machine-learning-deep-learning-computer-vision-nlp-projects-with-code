# CF Worker P0 Patches

`origin_signature: MrLiouWord`

Source-level and deployment-level patches for the three Cloudflare Workers with
P0 security findings surfaced by [`docs/STAGE3_WORKER_AUDIT_20260710.md`](../../docs/STAGE3_WORKER_AUDIT_20260710.md).

Each patch is a self-contained markdown file with: problem statement, diff, deployment
steps, and a verification checklist. **Nothing here re-embeds the current deployed
Worker source**; only the changed hunks are shown, with enough context to apply cleanly.

## Recommended order

Apply in increasing complexity so early wins are locked in before the biggest change:

| Order | Patch | Complexity | Est. time |
|---|---|---|---|
| 1 | [`particle-system-hub-P0.md`](./particle-system-hub-P0.md) | 1-line source + wrangler secret + 6-step rotation | 5 min |
| 2 | [`particle-ai-gateway-P0.md`](./particle-ai-gateway-P0.md) | ~10 line auth-guard block + wrangler.toml var | 15 min |
| 3 | [`particle-auth-gateway-P0.md`](./particle-auth-gateway-P0.md) | Cryptographic rewrite with versioned envelope + phased in-place migration | 2-3 hours |

## Shared principles

- **Rotation without reading the old value.** Where a live secret is exposed, generate the new value fresh and configure the upstream to accept both during transition; never `wrangler tail` or dashboard-view the old secret just to re-type it.
- **Backwards compatibility during migration.** Where format changes (patch #3), envelopes are versioned so pre- and post-migration data coexist.
- **Fail-closed defaults.** Any dev-only escape hatch must require two independent, explicit signals — never a single "true"/"1"/"on" flag.
- **Deploy → verify → revoke.** Every rotation ends by removing the old capability after the new one is proven — not before.

## Not covered here (future patches)

- `particle-doctor` — `CF_ACCOUNT` hardcoded (P2 hygiene, or P0/P1 if `CF_KEY` is Global). Priority depends on the CF_KEY scope; see `STAGE3_WORKER_AUDIT_20260710.md` §3.5.
- `shengai-isp` — `ANTHROPIC_API_KEY` hardcoded (flagged in CareOS report, not directly audited here).
- `particle-sig-verify` — currently a stub. Not a P0 (no vulnerable logic to leak), but a P1 replacement: port `MRL_AI_SYSTEM/particles/sig_verify/mrl_sig_verify.py` (Ed25519) to a CF Worker using WebCrypto's `Ed25519` sign/verify.
