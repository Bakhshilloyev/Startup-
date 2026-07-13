"""Runtime bootstrap: load configs, detect the platform, and wire the agent.

The result is a fully constructed, runnable Agent. This module is the place
where weak-device decisions (smaller models, reduced features) are applied.
"""

import os

from ..adapters import detect as detect_platform
from ..adapters.common import arch, env, paths
from ..core.agent import Agent
from ..core.executor import Executor
from ..core.planner import Planner
from ..core.safety import PolicyGuard
from ..core.tool_router import ToolRouter
from ..core.verifier import Verifier
from ..llm.client import build_llm
from ..llm.model_registry import ModelRegistry
from ..memory.long_term import LongTermMemory
from ..memory.short_term import ShortTermMemory
from ..memory.sqlite_store import SQLiteStore
from ..tools import dispatch_table
from ..tools.memory_tools import set_memory_store
from ..utils.yaml_lite import load_file


def _load_configs(configs_dir: str) -> dict:
    out = {}
    for name in ["default", "models", "tools", "routes", "permissions"]:
        p = os.path.join(configs_dir, f"{name}.yaml")
        if os.path.exists(p):
            out[name] = load_file(p) or {}
    return out


def detect_weak_device(platform_info: dict, arch_info: dict) -> bool:
    if platform_info.get("termux"):
        return True
    if arch_info.get("bits") == 32:
        return True
    try:
        pages = os.sysconf("SC_PHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
        mem_bytes = pages * page_size if pages and page_size else 0
        if 0 < mem_bytes < 2 * 1024 ** 3:
            return True
    except Exception:
        pass
    mode = os.environ.get("UNIFIED_WEAK_DEVICE")
    if mode == "1":
        return True
    if mode == "0":
        return False
    return False


def build(configs_dir: str | None = None, repo_root: str | None = None):
    repo_root = repo_root or os.getcwd()
    configs_dir = configs_dir or os.path.join(repo_root, "configs")
    cfg = _load_configs(configs_dir)
    default_cfg = cfg.get("default", {}) or {}
    raw_tools = cfg.get("tools", {}) or {}
    tools_cfg = raw_tools.get("tools", {}) or {}
    permissions = cfg.get("permissions", {}) or {}

    platform = detect_platform()
    platform_info = platform.info()
    arch_info = arch.summary()
    weak = default_cfg.get("weak_device_mode", "auto")
    weak_device = weak is True or (weak in ("auto", "true") and detect_weak_device(platform_info, arch_info))

    registry = ModelRegistry(cfg.get("models", {}) or {})
    provider = os.environ.get("UNIFIED_PROVIDER") or default_cfg.get("provider", "auto")
    model = os.environ.get("UNIFIED_MODEL") or default_cfg.get("model")
    api_key = os.environ.get("UNIFIED_API_KEY") or default_cfg.get("api_key")
    base_url = os.environ.get("UNIFIED_BASE_URL") or default_cfg.get("base_url")
    llm = build_llm(
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url,
        registry=registry,
        weak_device=weak_device,
    )

    memory_path = os.path.join(paths.ensure_dir(os.path.join(repo_root, "data", "memory")), "agent.db")
    store = SQLiteStore(memory_path)
    long_term = LongTermMemory(store)
    set_memory_store(long_term)
    short_term = ShortTermMemory(max_turns=int(default_cfg.get("max_steps", 50)))

    tool_router = ToolRouter(cfg.get("routes", {}))
    available = set(_enabled_tools(tools_cfg))
    planner = Planner(router=tool_router, llm=llm, available=available)
    safety = PolicyGuard(permissions)
    executor = Executor(
        safety=safety,
        platform=platform,
        llm=llm,
        dispatch=dispatch_table(),
        shell_timeout=int((raw_tools.get("shell") or {}).get("timeout", 60)),
        weak_device=weak_device,
    )
    verifier = Verifier()

    agent = Agent(
        name=default_cfg.get("name", "unified-agent"),
        planner=planner,
        executor=executor,
        verifier=verifier,
        short_term=short_term,
        long_term=long_term,
        platform=platform,
        llm=llm,
        config=default_cfg,
    )
    agent.weak_device = weak_device
    agent.platform_info = platform_info
    return agent


def _enabled_tools(tools_cfg: dict) -> list:
    from ..tools import names

    prefix_to_cfg = {
        "list": "file_tools",
        "read": "file_tools",
        "write": "file_tools",
        "edit": "file_tools",
        "glob": "file_tools",
        "grep": "file_tools",
        "run": "shell_tools",
        "fetch": "web_tools",
        "http": "api_tools",
        "remember": "memory_tools",
        "recall": "memory_tools",
    }
    enabled = []
    for n in names():
        cfg_key = None
        for prefix, key in prefix_to_cfg.items():
            if n.startswith(prefix):
                cfg_key = key
                break
        if cfg_key and tools_cfg.get(cfg_key, True):
            enabled.append(n)
    return enabled
