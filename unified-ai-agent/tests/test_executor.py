import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent.core.executor import Executor
from agent.core.planner import Planner
from agent.core.tool_router import ToolRouter
from agent.core.verifier import Verifier
from agent.core.safety import PolicyGuard
from agent.tools import names


class TestExecutor(unittest.TestCase):
    def setUp(self):
        self.router = ToolRouter()
        self.planner = Planner(router=self.router, available=set(names()))
        self.safety = PolicyGuard({"allow_shell": True})
        self.executor = Executor(safety=self.safety)
        self.verifier = Verifier()

    def test_execute_list_files(self):
        steps = self.planner.plan("list files in the current directory")
        self.executor.execute(steps)
        v = self.verifier.verify(steps, "x")
        self.assertEqual(v["done"], 1)
        self.assertEqual(v["failed"], 0)

    def test_blocked_command(self):
        from agent.core.safety import SafetyError

        guard = PolicyGuard({"allow_shell": True, "blocked_commands": ["rm -rf /"]})
        with self.assertRaises(SafetyError):
            guard.check_shell("rm -rf /")


if __name__ == "__main__":
    unittest.main()
