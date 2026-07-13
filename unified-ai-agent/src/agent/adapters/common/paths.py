"""Cross-platform path resolution for configuration, data, memory and logs."""

import os

from .env import is_termux, is_windows


def user_data_dir(app_name: str = "unified-agent") -> str:
    """Return a writable per-user data directory appropriate for the OS."""
    if is_termux():
        base = os.path.join(os.environ.get("HOME", ""), ".termux", app_name)
    elif is_windows():
        base = os.environ.get("APPDATA")
        if not base:
            base = os.path.join(os.path.expanduser("~"), "AppData", "Roaming")
        base = os.path.join(base, app_name)
    elif os.environ.get("XDG_DATA_HOME"):
        base = os.path.join(os.environ["XDG_DATA_HOME"], app_name)
    else:
        base = os.path.join(os.path.expanduser("~"), ".local", "share", app_name)
    return base


def user_config_dir(app_name: str = "unified-agent") -> str:
    if is_termux():
        return os.path.join(os.environ.get("HOME", ""), ".termux", app_name)
    if is_windows():
        base = os.environ.get("APPDATA")
        if not base:
            base = os.path.join(os.path.expanduser("~"), "AppData", "Roaming")
        return os.path.join(base, app_name)
    if os.environ.get("XDG_CONFIG_HOME"):
        return os.path.join(os.environ["XDG_CONFIG_HOME"], app_name)
    return os.path.join(os.path.expanduser("~"), ".config", app_name)


def repo_paths(repo_root: str | None = None) -> dict:
    """Resolve in-repo paths; falls back to current working directory.

    Using in-repo paths keeps the project self-contained and clone-and-run.
    """
    root = repo_root or os.getcwd()
    return {
        "root": root,
        "configs": os.path.join(root, "configs"),
        "prompts": os.path.join(root, "prompts"),
        "data": os.path.join(root, "data"),
        "memory": os.path.join(root, "data", "memory"),
        "cache": os.path.join(root, "data", "cache"),
        "logs": os.path.join(root, "data", "logs"),
    }


def ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path
