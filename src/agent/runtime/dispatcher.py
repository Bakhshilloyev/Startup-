"""Dispatcher: directly invoke a single tool by name with safety checks."""

from ..core.safety import PolicyGuard
from ..tools import dispatch_table


class Dispatcher:
    def __init__(self, safety: PolicyGuard | None = None, platform=None, shell_timeout=60):
        self.safety = safety or PolicyGuard()
        self.platform = platform
        self.shell_timeout = shell_timeout
        self.dispatch = dispatch_table()

    def call(self, name: str, args: dict):
        fn = self.dispatch.get(name)
        if fn is None:
            raise KeyError(f"no such tool: {name}")
        if name == "run_command":
            self.safety.check_shell(args.get("command", ""))
            return fn(args, platform=self.platform, timeout=self.shell_timeout, allowed=True)
        return fn(args)
