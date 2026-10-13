"""conftest.py for mother_platform tests.

origin_signature: MrLiouWord

讓 pytest 收 mother_platform/tests/ 時，自動把 `09_workflow` 加到 sys.path。
09_workflow 開頭有數字,不是合法 Python package 名,所以不能用 import。
這個 conftest.py 讓既有 tests 不用在每個檔案裡做 sys.path hack。
"""
import os
import sys

_WORKFLOW_DIR = os.path.join(os.path.dirname(__file__), "..", "09_workflow")
if _WORKFLOW_DIR not in sys.path:
    sys.path.insert(0, _WORKFLOW_DIR)
