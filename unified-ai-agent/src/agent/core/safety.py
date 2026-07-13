"""Policy guard: blocks unsafe commands and gated actions."""

from ..runtime.errors import SafetyError


class PolicyGuard:
    def __init__(self, permissions: dict | None = None):
        self.p = permissions or {}
        self.blocked = self.p.get("blocked_commands", []) or []
        self.allow_shell = self.p.get("allow_shell", True)
        self.allow_write = self.p.get("allow_write", True)
        self.allow_network = self.p.get("allow_network", False)
        self.require_confirmation = self.p.get("require_confirmation", False)

    def check_shell(self, command: str) -> bool:
        if not self.allow_shell:
            raise SafetyError("shell execution is disabled by policy")
        for pattern in self.blocked:
            if pattern and pattern in command:
                raise SafetyError(f"blocked command pattern: {pattern!r}")
        return True

    def check_write(self) -> bool:
        if not self.allow_write:
            raise SafetyError("write operations are disabled by policy")
        return True

    def check_network(self) -> bool:
        if not self.allow_network:
            raise SafetyError("network access is disabled by policy")
        return True
