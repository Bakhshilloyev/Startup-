"""Filesystem helpers used by tools and core modules."""

import os
import shutil


def is_writable(path: str) -> bool:
    if os.path.exists(path):
        return os.access(path, os.W_OK)
    parent = os.path.dirname(os.path.abspath(path))
    return os.access(parent, os.W_OK)


def safe_join(base: str, *parts: str) -> str:
    """Join paths and refuse to escape the base directory."""
    target = os.path.normpath(os.path.join(base, *parts))
    base_abs = os.path.abspath(base)
    if not (target == base_abs or target.startswith(base_abs + os.sep)):
        raise ValueError("path escapes base directory")
    return target


def human_size(num: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(num) < 1024.0:
            return f"{num:.1f}{unit}"
        num /= 1024.0
    return f"{num:.1f}PB"


def read_text(path: str, limit: int | None = None) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        data = fh.read()
    if limit:
        data = data[:limit]
    return data


def available_space(path: str = ".") -> int:
    try:
        return shutil.disk_usage(path).free
    except Exception:
        return 0
