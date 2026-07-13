"""Shell execution tools. Platform-aware via the runtime platform provider."""

import subprocess

from ..utils.validators import validate_args


def run_command(args, platform=None, timeout=60, allowed=True):
    a = validate_args(
        {
            "command": {"type": "str", "required": True},
            "cwd": {"type": "str", "required": False, "default": None},
        },
        args,
    )
    if not allowed:
        raise PermissionError("shell execution is disabled by policy")
    cmd = a["command"]
    if platform is not None:
        return platform.shell_run(cmd, cwd=a["cwd"], timeout=timeout)
    proc = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=a["cwd"]
    )
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run a shell command and return stdout/stderr/exit code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "cwd": {"type": "string"},
                },
                "required": ["command"],
            },
        },
    }
]

FN = {"run_command": run_command}
