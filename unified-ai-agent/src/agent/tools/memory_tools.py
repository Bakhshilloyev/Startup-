"""Memory-backed tools. The store is injected by the agent at runtime."""

from ..utils.validators import validate_args

_store = None


def set_memory_store(store):
    global _store
    _store = store


def remember(args):
    a = validate_args(
        {
            "key": {"type": "str", "required": True},
            "value": {"type": "str", "required": True},
        },
        args,
    )
    if _store is None:
        raise RuntimeError("memory store not initialized")
    _store.put(a["key"], a["value"])
    return {"remembered": a["key"]}


def recall(args):
    a = validate_args(
        {"key": {"type": "str", "required": False, "default": None}}, args
    )
    if _store is None:
        raise RuntimeError("memory store not initialized")
    if a["key"]:
        return {"key": a["key"], "value": _store.get(a["key"])}
    return {"recent": _store.search("", limit=20)}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "remember",
            "description": "Store a durable fact/key-value in long-term memory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "value": {"type": "string"},
                },
                "required": ["key", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recall",
            "description": "Recall a stored value, or list recent memories.",
            "parameters": {
                "type": "object",
                "properties": {"key": {"type": "string"}},
                "required": [],
            },
        },
    }
]

FN = {"remember": remember, "recall": recall}
