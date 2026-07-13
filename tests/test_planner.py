import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent.core.planner import Planner
from agent.core.tool_router import ToolRouter
from agent.tools import names


class TestPlanner(unittest.TestCase):
    def setUp(self):
        self.p = Planner(router=ToolRouter(), available=set(names()))

    def test_rule_plan_filesystem(self):
        steps = self.p.plan("list files in the current directory")
        self.assertEqual(len(steps), 1)
        self.assertEqual(steps[0]["intent"], "filesystem")
        self.assertIsNotNone(steps[0]["tool"])

    def test_rule_plan_shell(self):
        steps = self.p.plan("run: echo hi")
        self.assertEqual(steps[0]["intent"], "code_execution")
        self.assertEqual(steps[0]["args"]["command"], "echo hi")

    def test_general_fallback(self):
        steps = self.p.plan("summarize the meaning of life")
        self.assertEqual(steps[0]["intent"], "general")


if __name__ == "__main__":
    unittest.main()
