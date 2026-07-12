"""Tool system.

Goat can act on a real filesystem and shell - the "Claude Code" strength.
Every tool has an OpenAI-style JSON schema (also understood by Ollama and
Anthropic via conversion) plus a safe executor.

Tools are intentionally simple and dependency-free so they also run on weak
devices (Termux). Shell commands are sandboxed with a timeout and a working
directory.
"""

import json
import os
import subprocess
from pathlib import Path

MAX_FILE_CHARS = 200_000
CMD_TIMEOUT = 120
LINE_LIMIT = 2000


def _resolve(cwd: str, path: str) -> Path:
    p = Path(path)
    if not p.is_absolute():
        p = Path(cwd) / p
    return p.resolve()


def read_file(cwd: str, path: str, offset: int = 0, limit: int = 0) -> str:
    try:
        p = _resolve(cwd, path)
        if not p.exists():
            return f"[error] file not found: {path}"
        if p.is_dir():
            return f"[error] {path} is a directory, use list_files"
        text = p.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        start = max(0, offset)
        end = start + (limit or len(lines))
        window = lines[start:end]
        body = "\n".join(window)
        if len(body) > MAX_FILE_CHARS:
            body = body[:MAX_FILE_CHARS] + "\n...[truncated]"
        total = len(lines)
        return f"(lines {start+1}-{min(end, total)} of {total})\n{body}"
    except Exception as exc:  # pragma: no cover
        return f"[error] {exc}"


def write_file(cwd: str, path: str, content: str) -> str:
    try:
        p = _resolve(cwd, path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"[ok] wrote {len(content)} chars to {path}"
    except Exception as exc:  # pragma: no cover
        return f"[error] {exc}"


def edit_file(cwd: str, path: str, old_string: str, new_string: str) -> str:
    try:
        p = _resolve(cwd, path)
        if not p.exists():
            return f"[error] file not found: {path}"
        text = p.read_text(encoding="utf-8", errors="replace")
        if old_string not in text:
            return "[error] old_string not found (must match exactly, including whitespace)"
        count = text.count(old_string)
        if count > 1:
            return (
                f"[error] old_string is not unique ({count} occurrences); "
                "provide more surrounding context"
            )
        text = text.replace(old_string, new_string, 1)
        p.write_text(text, encoding="utf-8")
        return f"[ok] edited {path}"
    except Exception as exc:  # pragma: no cover
        return f"[error] {exc}"


def list_files(cwd: str, path: str = ".", recursive: bool = False) -> str:
    try:
        p = _resolve(cwd, path)
        if not p.exists():
            return f"[error] path not found: {path}"
        items = []
        iterator = p.rglob("*") if recursive else p.glob("*")
        for child in sorted(iterator):
            if any(part.startswith(".") for part in child.relative_to(p).parts):
                continue
            tag = "d" if child.is_dir() else "f"
            items.append(f"{tag} {str(child.relative_to(p))}")
        out = "\n".join(items) if items else "(empty)"
        return f"{path}:\n{out}"
    except Exception as exc:  # pragma: no cover
        return f"[error] {exc}"


def glob_files(cwd: str, pattern: str, path: str = ".") -> str:
    try:
        p = _resolve(cwd, path)
        matches = sorted(str(m.relative_to(p)) for m in p.glob(pattern))
        return "\n".join(matches) if matches else "(no matches)"
    except Exception as exc:  # pragma: no cover
        return f"[error] {exc}"


def grep_files(cwd: str, pattern: str, path: str = ".", include: str = "") -> str:
    import re

    try:
        p = _resolve(cwd, path)
        rx = re.compile(pattern)
        results = []
        for root, dirs, files in os.walk(p):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for f in files:
                if f.startswith("."):
                    continue
                if include and not f.endswith(tuple(include.split(","))):
                    continue
                fp = Path(root) / f
                try:
                    for i, line in enumerate(
                        fp.read_text(encoding="utf-8", errors="ignore").splitlines(),
                        start=1,
                    ):
                        if rx.search(line):
                            results.append(f"{fp.relative_to(p)}:{i}: {line}")
                except Exception:
                    continue
                if len(results) > 500:
                    break
        return "\n".join(results) if results else "(no matches)"
    except Exception as exc:  # pragma: no cover
        return f"[error] {exc}"


def run_command(cwd: str, command: str, timeout: int = CMD_TIMEOUT) -> str:
    try:
        proc = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        out = []
        if proc.stdout:
            out.append(proc.stdout)
        if proc.stderr:
            out.append(f"[stderr]\n{proc.stderr}")
        out.append(f"[exit code {proc.returncode}]")
        combined = "\n".join(out)
        if len(combined) > MAX_FILE_CHARS:
            combined = combined[:MAX_FILE_CHARS] + "\n...[truncated]"
        return combined
    except subprocess.TimeoutExpired:
        return f"[error] command timed out after {timeout}s"
    except Exception as exc:  # pragma: no cover
        return f"[error] {exc}"


# --- Tool registry -------------------------------------------------------

TOOLS = {
    "read_file": read_file,
    "write_file": write_file,
    "edit_file": edit_file,
    "list_files": list_files,
    "glob_files": glob_files,
    "grep_files": grep_files,
    "run_command": run_command,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from disk. Returns line-numbered content. "
            "Use offset/limit to read a slice for large files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file."},
                    "offset": {
                        "type": "integer",
                        "description": "0-based starting line.",
                        "default": 0,
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max number of lines to return (0 = all).",
                        "default": 0,
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create or overwrite a file with the given content. "
            "Creates parent directories as needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file."},
                    "content": {
                        "type": "string",
                        "description": "Full file content to write.",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Replace an exact, unique substring in a file with new "
            "text. The old_string must match exactly and occur once.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file."},
                    "old_string": {
                        "type": "string",
                        "description": "Exact text to replace.",
                    },
                    "new_string": {
                        "type": "string",
                        "description": "Replacement text.",
                    },
                },
                "required": ["path", "old_string", "new_string"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories in a path. Set recursive "
            "to include nested entries.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path."},
                    "recursive": {
                        "type": "boolean",
                        "description": "List recursively.",
                        "default": False,
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "glob_files",
            "description": "Find files matching a glob pattern (e.g. '**/*.py').",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Glob pattern."},
                    "path": {
                        "type": "string",
                        "description": "Base directory.",
                        "default": ".",
                    },
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep_files",
            "description": "Search file contents with a regular expression.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Regex pattern."},
                    "path": {
                        "type": "string",
                        "description": "Directory to search.",
                        "default": ".",
                    },
                    "include": {
                        "type": "string",
                        "description": "Comma-separated file extensions, e.g. '.py,.js'.",
                        "default": "",
                    },
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Execute a shell command in the working directory and "
            "return combined stdout/stderr plus the exit code. Use for builds, "
            "tests, git, and environment inspection.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to run.",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds.",
                        "default": CMD_TIMEOUT,
                    },
                },
                "required": ["command"],
            },
        },
    },
]


def dispatch(name: str, arguments: str, cwd: str) -> str:
    """Run a tool by name with a JSON argument string."""
    fn = TOOLS.get(name)
    if not fn:
        return f"[error] unknown tool: {name}"
    try:
        kwargs = json.loads(arguments) if arguments else {}
    except json.JSONDecodeError as exc:
        return f"[error] invalid JSON arguments: {exc}"
    try:
        return fn(cwd, **kwargs)
    except TypeError as exc:
        return f"[error] bad arguments for {name}: {exc}"
