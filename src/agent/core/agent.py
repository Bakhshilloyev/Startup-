"""The agent: high-level orchestrator wiring planner, executor and memory."""

from ..memory.long_term import LongTermMemory
from ..memory.short_term import ShortTermMemory
from .workflow import Workflow


class Agent:
    def __init__(
        self,
        name: str = "goat-agent",
        planner=None,
        executor=None,
        verifier=None,
        short_term: ShortTermMemory | None = None,
        long_term: LongTermMemory | None = None,
        platform=None,
        llm=None,
        config: dict | None = None,
    ):
        self.name = name
        self.planner = planner
        self.executor = executor
        self.verifier = verifier
        self.short_term = short_term or ShortTermMemory()
        self.long_term = long_term
        self.platform = platform
        self.llm = llm
        self.config = config or {}
        self.workflow = Workflow(planner, executor, verifier)
        self.session_id = None

    def set_session(self, session_id: str):
        self.session_id = session_id

    def run(self, task: str, context: dict | None = None) -> dict:
        base = {
            "platform": self.platform.info() if self.platform else {},
            "session_id": self.session_id,
        }
        if context:
            base.update(context)
        result = self.workflow.run(task, base)
        self.short_term.add("user", task)
        self.short_term.add("assistant", _summarize(result))
        if self.long_term is not None:
            try:
                self.long_term.remember(
                    f"task:{abs(hash(task))}", result["verification"]["summary"]
                )
            except Exception:
                pass
        return result

    @property
    def offline(self) -> bool:
        return self.llm is None


def _summarize(result: dict) -> str:
    v = result.get("verification", {})
    return f"[{v.get('summary')}] {result.get('task')}"
