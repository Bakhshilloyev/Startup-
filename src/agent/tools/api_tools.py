"""Generic API request tool."""

import json

from ..utils.validators import validate_args


def http_request(args):
    a = validate_args(
        {
            "url": {"type": "str", "required": True},
            "method": {"type": "str", "required": False, "default": "GET"},
            "headers": {"type": "str", "required": False, "default": "{}"},
            "body": {"type": "str", "required": False, "default": None},
            "timeout": {"type": "int", "required": False, "default": 30},
        },
        args,
    )
    method = a["method"].upper()
    headers = json.loads(a["headers"]) if a["headers"] else {}
    data = a["body"].encode("utf-8") if a["body"] else None

    try:
        import requests  # type: ignore

        r = requests.request(method, a["url"], headers=headers, data=data, timeout=a["timeout"])
        return {"status": r.status_code, "text": r.text[:8000]}
    except ImportError:
        import urllib.request

        req = urllib.request.Request(a["url"], data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=a["timeout"]) as resp:
                return {"status": resp.status, "text": resp.read().decode("utf-8", "replace")[:8000]}
        except Exception as exc:  # noqa: B902
            return {"status": 0, "error": str(exc)}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "http_request",
            "description": "Make an HTTP request to any JSON API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "method": {"type": "string"},
                    "headers": {"type": "string"},
                    "body": {"type": "string"},
                    "timeout": {"type": "integer"},
                },
                "required": ["url"],
            },
        },
    }
]

FN = {"http_request": http_request}
