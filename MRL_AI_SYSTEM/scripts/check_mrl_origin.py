#!/usr/bin/env python3
"""Protect MRL naming and original provenance. origin_signature: MrLiouWord"""
from pathlib import Path
import json
import sys
ROOT = Path(__file__).resolve().parents[2]
EXPECTED = json.loads("[{\"path\":\".github/workflows/mrl-ai-system-ci.yml\",\"count\":1,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/README.md\",\"count\":2,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/docs/ARCHITECTURE.md\",\"count\":1,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/docs/MRL_DELIVERY_MANIFEST_20260531.md\",\"count\":1,\"history\":true},{\"path\":\"MRL_AI_SYSTEM/edge_workers/ai_gateway/src/index.js\",\"count\":4,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/edge_workers/auth_gateway/src/index.js\",\"count\":4,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/edge_workers/sig_verify/README.md\",\"count\":1,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/edge_workers/sig_verify/src/index.js\",\"count\":2,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/mother_platform/09_workflow/MRL_MCP_Server_v1.py\",\"count\":2,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/mother_platform/09_workflow/MRL_MotherGateway_Adapter_v1.py\",\"count\":3,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/mother_platform/09_workflow/MRL_PerceptionGuardrail_Classifier_v1.py\",\"count\":3,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/mother_platform/09_workflow/MRL_SemanticEmbedding_Core_v1.py\",\"count\":3,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/mother_platform/MRL_DELIVERY_MANIFEST_20260531.md\",\"count\":1,\"history\":true},{\"path\":\"MRL_AI_SYSTEM/mother_platform/MRL_ParticleArchive/External/MRL_AbsorbedArtifacts_20260531/MRL_Absorption_Ledger_v1.yaml\",\"count\":4,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/mother_platform/MRL_ParticleArchive/External/MRL_AbsorbedArtifacts_20260531/MRL_SystemRegistry_Config_v1.yaml\",\"count\":1,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/mother_platform/MRL_Platform_Server.py\",\"count\":4,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/mother_platform/tests/test_MRL_mother_gateway_adapter.py\",\"count\":2,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/mother_platform/tests/test_MRL_perception_classifier.py\",\"count\":2,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/mother_platform/tests/test_MRL_semantic_embedding.py\",\"count\":3,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/particles/boot/boot.manifest.json\",\"count\":1,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/particles/boot/mrl_boot.py\",\"count\":1,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/particles/doctor/mrl_doctor.py\",\"count\":2,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/particles/sig_verify/mrl_sig_verify.py\",\"count\":2,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/particles/smartbody_v2/mrl_smartbody.py\",\"count\":2,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/particles/system_hub/mrl_system_hub.py\",\"count\":2,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/particles/trace_chain/mrl_trace.py\",\"count\":2,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/relay_station/src/MRL_Core.js\",\"count\":1,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/relay_station/src/MRL_RelayStation.js\",\"count\":1,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/relay_station/test/MRL_acceptance_test.js\",\"count\":1,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/tests/test_smartbody.py\",\"count\":1,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/docs/MRL_Naming_Law.md\",\"count\":3,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/edge_workers/README.md\",\"count\":2,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/edge_workers/patches/README.md\",\"count\":1,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/edge_workers/patches/particle-ai-gateway-P0.md\",\"count\":1,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/edge_workers/patches/particle-auth-gateway-P0.md\",\"count\":2,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/edge_workers/patches/particle-system-hub-P0.md\",\"count\":2,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/edge_workers/patches/shengai-isp-P0.md\",\"count\":1,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/mother_platform/tests/conftest.py\",\"count\":1,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/scripts/check_naming_law.sh\",\"count\":1,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/scripts/check_secrets.sh\",\"count\":1,\"history\":false},{\"path\":\"MRL_AI_SYSTEM/scripts/verify_all.sh\",\"count\":1,\"history\":false}]")
def inspect(text, rule):
    errors = []
    if "MrliouAI" in text:
        errors.append("product identity must not replace origin_signature")
    if text.count("MrLiouWord") < rule["count"]:
        errors.append("original MrLiouWord identity removed")
    if rule["history"]:
        for value in ("交付分支: claude/memory-system-rules-prep-EuBXH (HEAD=5b8acd8)", "origin/claude/memory-system-rules-prep-EuBXH", "僅 claude/ 側分支"):
            if value not in text:
                errors.append("historical branch provenance changed: " + value)
    return errors
def main():
    errors = []
    for rule in EXPECTED:
        path = ROOT / rule["path"]
        if not path.is_file():
            errors.append(rule["path"] + ": missing original path")
            continue
        errors.extend(rule["path"] + ": " + e for e in inspect(path.read_text(encoding="utf-8"), rule))
    boot = json.loads((ROOT / "MRL_AI_SYSTEM/particles/boot/boot.manifest.json").read_text(encoding="utf-8"))
    if boot.get("origin_signature") != "MrLiouWord":
        errors.append("boot manifest origin_signature must be MrLiouWord")
    relay = (ROOT / "MRL_AI_SYSTEM/relay_station/src/MRL_Core.js").read_text(encoding="utf-8")
    if "MRL_Particle_Mother_RelayStation_v1" not in relay or "namespace: 'MRL_'" not in relay:
        errors.append("MRL relay system_name or namespace removed")
    for error in errors:
        print("[FAIL] " + error)
    if errors:
        return 1
    print("MRL_NAMING_RESTORATION_PASS: " + str(len(EXPECTED)) + " original paths")
    return 0
if __name__ == "__main__":
    sys.exit(main())
