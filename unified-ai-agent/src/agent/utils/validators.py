"""Input validators for tool arguments and configuration."""

from typing import Any


def require(condition: bool, message: str):
    if not condition:
        raise ValueError(message)


def is_nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def is_int_in(value: Any, low: int, high: int) -> bool:
    return isinstance(value, int) and low <= value <= high


def validate_args(schema: dict, args: dict) -> dict:
    """Validate args against a simple schema.

    schema: {name: {"type": str, "required": bool, "default": any}}
    Returns a normalized args dict.
    """
    out = {}
    for name, spec in schema.items():
        present = name in args and args[name] is not None
        if not present:
            if spec.get("required"):
                raise ValueError(f"missing required argument: {name}")
            out[name] = spec.get("default")
            continue
        value = args[name]
        expected = spec.get("type", "str")
        if expected == "int" and not isinstance(value, int):
            raise ValueError(f"{name} must be int")
        if expected == "str" and not isinstance(value, str):
            raise ValueError(f"{name} must be str")
        if expected == "bool" and not isinstance(value, bool):
            raise ValueError(f"{name} must be bool")
        if expected == "list" and not isinstance(value, list):
            raise ValueError(f"{name} must be list")
        out[name] = value
    return out
