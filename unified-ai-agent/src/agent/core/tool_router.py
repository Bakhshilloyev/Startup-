"""Tool router: maps intents to tools and detects intent from free text."""

import re

from ..utils.validators import require


class ToolRouter:
    DEFAULT_ROUTES = {
        "filesystem": [
            "list_files",
            "read_file",
            "write_file",
            "edit_file",
            "glob_files",
            "grep_files",
        ],
        "code_execution": ["run_command"],
        "web_research": ["fetch_url"],
        "api_call": ["http_request"],
        "memory": ["remember", "recall"],
    }

    def __init__(self, config: dict | None = None):
        self.routes = dict(self.DEFAULT_ROUTES)
        for r in (config or {}).get("routes", []) or []:
            self.routes[r.get("intent")] = r.get("tools", [])

    def route(self, intent: str) -> list:
        return self.routes.get(intent, [])

    def detect_intent(self, text: str) -> str:
        t = (text or "").lower()
        if any(k in t for k in ["http://", "https://", "fetch", "web", "browse", "url"]):
            return "web_research"
        if any(k in t for k in ["remember", "recall", "memory", "note", "remind"]):
            return "memory"
        if any(k in t for k in ["run", "execute", "command", "shell", "install", "pip", "terminal"]):
            return "code_execution"
        if any(
            k in t
            for k in ["read", "write", "file", "list", "grep", "edit", "glob", "directory", "folder"]
        ):
            return "filesystem"
        return "general"

    def pick_tool(self, intent: str, available: set) -> str | None:
        for tool in self.route(intent):
            if tool in available:
                return tool
        return None


def extract_url(text: str):
    m = re.search(r"https?://[^\s]+", text)
    return m.group(0) if m else None


def extract_path(text: str):
    m = re.search(r"[\"']?([\w./\-]+\.[\w]+)[\"']?", text)
    return m.group(1) if m else None


def extract_command(text: str):
    t = text.strip()
    if t.lower().startswith("run"):
        return t.split(":", 1)[-1].strip() if ":" in t else t[3:].strip()
    return t
