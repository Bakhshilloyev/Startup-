import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent.runtime.bootstrap import build
from agent.api.routes import dispatch


class TestAPI(unittest.TestCase):
    def setUp(self):
        here = os.path.dirname(__file__)
        repo = os.path.abspath(os.path.join(here, ".."))
        self.agent = build(repo_root=repo)

    def test_health(self):
        code, body = dispatch(self.agent, "GET", "/health", {})
        self.assertEqual(code, 200)
        self.assertEqual(body["status"], "ok")

    def test_run(self):
        code, body = dispatch(self.agent, "POST", "/run", {"task": "list files in the current directory"})
        self.assertEqual(code, 200)
        self.assertTrue(body["verification"]["done"] >= 1)

    def test_run_missing_task(self):
        code, _ = dispatch(self.agent, "POST", "/run", {})
        self.assertEqual(code, 400)


if __name__ == "__main__":
    unittest.main()
