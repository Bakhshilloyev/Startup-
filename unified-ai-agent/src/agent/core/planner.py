"""Planner: turns a task into an ordered list of executable steps.

Two modes:
  * LLM mode  — asks the model for a structured plan (JSON steps).
  * Rule mode — deterministic intent detection + heuristic argument building.
Rule mode lets the agent run fully offline on weak devices.
"""

import json

from ..utils.json import try_parse
from .tool_router import (
    ToolRouter,
    extract_command,
    extract_path,
    extract_url,
)


class Planner:
    def __init__(self, router: ToolRouter | None = None, llm=None, available=None):
        self.router = router or ToolRouter()
        self.llm = llm
        self.available = available or set()

    def plan(self, task: str, max_steps: int = 12) -> list:
        intent = self.router.detect_intent(task)
        if self.llm is not None:
            steps = self._plan_with_llm(task, intent)
            if steps:
                return steps[:max_steps]
        return self._plan_rule_based(task, intent, max_steps)

    def _args_for(self, task: str, intent: str) -> dict:
        if intent == "web_research":
            return {"url": extract_url(task) or "https://example.com"}
        if intent == "code_execution":
            return {"command": extract_command(task)}
        if intent == "filesystem":
            path = extract_path(task)
            if "list" in task.lower() or "directory" in task.lower():
                return {"path": (path and path.rsplit("/", 1)[0]) or ".", "recursive": False}
            if path:
                return {"path": path}
            return {"path": ".", "recursive": False}
        if intent == "memory":
            return {"key": None}
        return {}

    def _plan_rule_based(self, task: str, intent: str, max_steps: int) -> list:
        if intent == "general":
            return [
                {
                    "id": 1,
                    "description": f"Analyze and respond to: {task}",
                    "intent": "general",
                    "tool": None,
                    "args": {},
                    "status": "pending",
                    "result": None,
                    "error": None,
                }
            ]
        tool = self.router.pick_tool(intent, self.available)
        step = {
            "id": 1,
            "description": f"{intent} task: {task}",
            "intent": intent,
            "tool": tool,
            "args": self._args_for(task, intent),
            "status": "pending",
            "result": None,
            "error": None,
        }
        return [step][:max_steps]

    def _plan_with_llm(self, task: str, intent: str) -> list:
        schema = {
            "type": "function",
            "function": {
                "name": "make_plan",
                "description": "Return an ordered plan as a JSON list of steps.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "steps": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "description": {"type": "string"},
                                    "intent": {"type": "string"},
                                    "tool": {"type": "string"},
                                    "args": {"type": "object"},
                                },
                            },
                        }
                    },
                    "required": ["steps"],
                },
            },
        }
        messages = [
            {"role": "system", "content": PLANNER_SYSTEM},
            {"role": "user", "content": f"Task: {task}\nDetected intent: {intent}"},
        ]
        try:
            resp = self.llm.chat(messages, tools=[schema], max_tokens=1024)
        except Exception:
            return []
        for call in resp.get("tool_calls", []):
            args = call.get("function", {}).get("arguments", "")
            data = try_parse(args)
            if isinstance(data, dict) and data.get("steps"):
                steps = data["steps"]
                for i, s in enumerate(steps, 1):
                    s.setdefault("id", i)
                    s.setdefault("status", "pending")
                    s.setdefault("result", None)
                    s.setdefault("error", None)
                    s.setdefault("args", {})
                return steps
        return []


PLANNER_SYSTEM = (
    "You are a task planner for a cross-platform AI agent. Break the user's "
    "task into small, ordered, executable steps. Each step must reference a "
    "tool from: list_files, read_file, write_file, edit_file, glob_files, "
    "grep_files, run_command, fetch_url, http_request, remember, recall. "
    "Prefer the smallest number of steps that accomplish the goal."
)
