"""Workflow engine: orchestrates planner -> executor -> verifier for one task."""

import time

from .executor import Executor
from .planner import Planner
from .verifier import Verifier


class Workflow:
    def __init__(self, planner: Planner, executor: Executor, verifier: Verifier):
        self.planner = planner
        self.executor = executor
        self.verifier = verifier

    def run(self, task: str, context: dict | None = None) -> dict:
        t0 = time.time()
        steps = self.planner.plan(task)
        self.executor.execute(steps, context)
        verification = self.verifier.verify(steps, task)
        return {
            "task": task,
            "steps": steps,
            "verification": verification,
            "elapsed_s": round(time.time() - t0, 3),
        }
