"""Web tools (URL fetch). Uses requests if available, else stdlib urllib."""

import json

from ..utils.validators import validate_args


def _http_get(url, timeout, headers):
    try:
        import requests  # type: ignore

        r = requests.get(url, timeout=timeout, headers=headers)
        return r.status_code, r.text
    except ImportError:
        import urllib.request

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")


def fetch_url(args):
    a = validate_args(
        {
            "url": {"type": "str", "required": True},
            "timeout": {"type": "int", "required": False, "default": 30},
            "max_chars": {"type": "int", "required": False, "default": 8000},
        },
        args,
    )
    headers = {"User-Agent": "unified-agent/0.1"}
    status, text = _http_get(a["url"], a["timeout"], headers)
    return {
        "status": status,
        "url": a["url"],
        "text": text[: a["max_chars"]],
        "truncated": len(text) > a["max_chars"],
    }


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Fetch a web page or API URL and return its text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "timeout": {"type": "integer"},
                    "max_chars": {"type": "integer"},
                },
                "required": ["url"],
            },
        },
    }
]

FN = {"fetch_url": fetch_url}
