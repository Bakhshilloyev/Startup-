"""Configuration for Goat.

Configuration is loaded from (in order of precedence, highest first):

1. Environment variables (``GOAT_*``)
2. A config file at ``~/.goat/config.toml``
3. Built-in adaptive defaults based on the detected platform

No key is required to *start* Goat; sensible defaults are picked so the agent
works out of the box on weak devices (Termux) and strong workstations alike.
"""

import os
from pathlib import Path

from . import platform as plat

DEFAULT_CONFIG_DIR = Path(os.path.expanduser("~")) / ".goat"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.toml"


def _toml_load(path: Path) -> dict:
    """Best-effort TOML parse without forcing a dependency on ``tomllib``."""
    try:
        import tomllib  # Python >= 3.11

        with open(path, "rb") as fh:
            return tomllib.load(fh)
    except ModuleNotFoundError:
        try:
            import tomli  # optional backport for < 3.11

            with open(path, "rb") as fh:
                return tomli.load(fh)
        except ModuleNotFoundError:
            # Minimal hand-rolled parser for the flat [section] key = "value"
            # layout Goat writes. Good enough and dependency-free.
            return _mini_toml(path)


def _mini_toml(path: Path) -> dict:
    data: dict = {}
    section = ""
    text = path.read_text(encoding="utf-8")
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            data.setdefault(section, {})
            continue
        if "=" in line and section:
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip()
            if val.startswith('"'):
                end = val.find('"', 1)
                val = val[1:end] if end != -1 else val.strip('"')
            elif val.startswith("'"):
                end = val.find("'", 1)
                val = val[1:end] if end != -1 else val.strip("'")
            else:
                h = val.find("#")
                if h != -1:
                    val = val[:h].strip()
            data[section][key] = val
    return data


def _coerce(val):
    if isinstance(val, str):
        low = val.lower()
        if low in ("true", "yes", "1"):
            return True
        if low in ("false", "no", "0"):
            return False
        try:
            return int(val)
        except ValueError:
            return val
    return val


class Config:
    """Holds merged, resolved configuration."""

    def __init__(self, data: dict):
        self.data = data

    def get(self, key, default=None, section="goat"):
        return self.data.get(section, {}).get(key, default)

    def provider(self) -> str:
        return self.get("provider", "auto")

    def model(self) -> str:
        return self.get("model", "")

    def api_key(self) -> str:
        return self.get("api_key", "")

    def base_url(self) -> str:
        return self.get("base_url", "")

    def temperature(self) -> float:
        return float(self.get("temperature", 0.2))

    def max_tokens(self) -> int:
        return int(self.get("max_tokens", 2048))

    def max_tool_rounds(self) -> int:
        return int(self.get("max_tool_rounds", 32))

    def cwd(self) -> str:
        return self.get("cwd", os.getcwd())

    def autostart(self) -> bool:
        return bool(self.get("autostart", True))

    def verbose(self) -> bool:
        return bool(self.get("verbose", False))

    def to_dict(self) -> dict:
        return self.data


def default_config() -> dict:
    """Adaptive defaults chosen from the detected platform."""
    p = plat.detect()
    # Strong devices can afford a bigger context window and more tokens.
    max_tokens = 1024 if p["weak_device"] else 2048
    provider = "ollama" if p["weak_device"] else "auto"
    model = "qwen2.5-coder:7b" if p["weak_device"] else ""
    return {
        "goat": {
            "provider": provider,
            "model": model,
            "api_key": "",
            "base_url": "" if p["weak_device"] else "",
            "temperature": 0.2,
            "max_tokens": max_tokens,
            "max_tool_rounds": 32,
            "cwd": os.getcwd(),
            "autostart": True,
            "verbose": False,
            "telegram_token": "",
            "telegram_allowed": "",
        }
    }


def load_config(path: Path = DEFAULT_CONFIG_FILE) -> Config:
    """Load config: defaults <- file <- environment."""
    cfg = default_config()
    if path.exists():
        try:
            file_cfg = _toml_load(path)
            # merge flat sections into goat section
            for section, vals in file_cfg.items():
                cfg["goat"].update({k: _coerce(v) for k, v in vals.items()})
        except Exception as exc:  # pragma: no cover - defensive
            print(f"[warn] could not parse config {path}: {exc}")

    # Environment overrides (GOAT_PROVIDER, GOAT_MODEL, GOAT_API_KEY, ...)
    env_map = {
        "GOAT_PROVIDER": "provider",
        "GOAT_MODEL": "model",
        "GOAT_API_KEY": "api_key",
        "GOAT_BASE_URL": "base_url",
        "GOAT_TEMPERATURE": "temperature",
        "GOAT_MAX_TOKENS": "max_tokens",
        "GOAT_CWD": "cwd",
        "GOAT_VERBOSE": "verbose",
    }
    for env_key, cfg_key in env_map.items():
        if env_key in os.environ:
            cfg["goat"][cfg_key] = _coerce(os.environ[env_key])

    return Config(cfg)


def ensure_config_dir() -> Path:
    DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return DEFAULT_CONFIG_DIR
