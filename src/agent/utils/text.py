"""Small text helpers (token counting, truncation, safe formatting)."""

import re


def count_tokens(text: str) -> int:
    """Rough token estimate; good enough for context budgeting on weak devices."""
    if not text:
        return 0
    return max(1, len(text) // 4)


def truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 40] + "\n...[truncated %d chars]" % (len(text) - max_chars + 40)


def strip_code_fences(text: str) -> str:
    fence = re.match(r"^\s*```[a-zA-Z0-9_-]*\n(.*)\n```\s*$", text, re.DOTALL)
    return fence.group(1) if fence else text


def to_lines(text: str):
    return [line for line in text.splitlines() if line.strip()]


def safe_format(template: str, **kwargs) -> str:
    try:
        return template.format(**kwargs)
    except Exception:
        return template
