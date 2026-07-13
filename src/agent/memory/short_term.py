"""Short-term (in-session) conversation memory with a rolling window."""


class ShortTermMemory:
    def __init__(self, max_turns: int = 50):
        self.max_turns = max_turns
        self.history = []

    def add(self, role: str, content, tool_calls=None, tool_call_id=None, name=None):
        self.history.append(
            {
                "role": role,
                "content": content,
                "tool_calls": tool_calls,
                "tool_call_id": tool_call_id,
                "name": name,
            }
        )
        if len(self.history) > self.max_turns * 2:
            self.history = self.history[-self.max_turns * 2 :]

    def get(self):
        return list(self.history)

    def clear(self):
        self.history = []

    def count_tokens(self) -> int:
        return sum(len(str(m.get("content", ""))) // 4 for m in self.history)
