"""MRL naming regression tests. origin_signature: MrLiouWord"""
import importlib.util
from pathlib import Path
import unittest
spec = importlib.util.spec_from_file_location("mrl_naming", Path(__file__).resolve().parents[1] / "scripts/check_mrl_origin.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
class NamingTests(unittest.TestCase):
    def test_original_origin_passes(self):
        self.assertEqual(m.inspect('origin_signature: MrLiouWord', {"count": 1, "history": False}), [])
    def test_product_name_cannot_replace_origin(self):
        self.assertTrue(m.inspect('origin_signature: MrliouAI', {"count": 1, "history": False}))
    def test_signature_deletion_fails(self):
        self.assertTrue(m.inspect('origin_signature: ""', {"count": 1, "history": False}))
    def test_historical_branch_rewrite_fails(self):
        original = 'origin_signature: MrLiouWord\n交付分支: claude/memory-system-rules-prep-EuBXH (HEAD=5b8acd8)\norigin/claude/memory-system-rules-prep-EuBXH\n僅 claude/ 側分支'
        rule = {"count": 1, "history": True}
        self.assertEqual(m.inspect(original, rule), [])
        self.assertTrue(m.inspect(original.replace('claude/', 'MrliouAI/'), rule))
if __name__ == "__main__":
    unittest.main()
