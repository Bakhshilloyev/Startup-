import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent.core.tool_router import ToolRouter


class TestRouter(unittest.TestCase):
    def setUp(self):
        self.r = ToolRouter()

    def test_detect_filesystem(self):
        self.assertEqual(self.r.detect_intent("read the file main.py"), "filesystem")

    def test_detect_shell(self):
        self.assertEqual(self.r.detect_intent("run: ls -la"), "code_execution")

    def test_detect_web(self):
        self.assertEqual(self.r.detect_intent("fetch https://x.com"), "web_research")

    def test_pick_tool(self):
        self.assertEqual(self.r.pick_tool("filesystem", {"list_files"}), "list_files")
        self.assertIsNone(self.r.pick_tool("filesystem", set()))


if __name__ == "__main__":
    unittest.main()
