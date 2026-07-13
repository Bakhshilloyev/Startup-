"""Executor: runs planned steps, routing to tools and guarding with policy."""

from ..runtime.errors import SafetyError, ToolError
from ..tools import dispatch_table
from .tool_router import extract_command


class Executor:
    def __init__(
        self,
        safety,
        platform=None,
        llm=None,
        dispatch=None,
        shell_timeout: int = 60,
        weak_device: bool = False,
    ):
        self.safety = safety
        self.platform = platform
        self.llm = llm
        self.dispatch = dispatch or dispatch_table()
        self.shell_timeout = shell_timeout
        self.weak_device = weak_device

    def execute(self, steps: list, context: dict | None = None) -> list:
        for step in steps:
            self._run_step(step, context or {})
        return steps

    def _run_step(self, step: dict, context: dict) -> None:
        tool = step.get("tool")
        if not tool:
            self._run_general(step, context)
            return
        fn = self.dispatch.get(tool)
        if fn is None:
            step["status"] = "failed"
            step["error"] = f"unknown tool: {tool}"
            return
        try:
            args = step.get("args", {}) or {}
            if tool == "run_command":
                self.safety.check_shell(args.get("command", ""))
                step["result"] = fn(
                    args,
                    platform=self.platform,
                    timeout=self.shell_timeout,
                    allowed=True,
                )
            else:
                step["result"] = fn(args)
            step["status"] = "done"
        except SafetyError as e:
            step["status"] = "failed"
            step["error"] = f"safety: {e}"
        except Exception as e:  # noqa: B902
            step["status"] = "failed"
            step["error"] = str(e) or type(e).__name__

    def _run_general(self, step: dict, context: dict) -> None:
        if self.llm is not None:
            try:
                resp = self.llm.chat(
                    [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": step.get("description", "")},
                    ]
                )
                step["result"] = {"answer": resp.get("text", "")}
                step["status"] = "done"
                return
            except Exception as e:  # noqa: B902
                step["status"] = "failed"
                step["error"] = f"llm: {e}"
                return
        step["status"] = "skipped"
        step["result"] = "no tool and no LLM configured (offline general step)"
