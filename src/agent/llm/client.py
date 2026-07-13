"""Goat LLM client factory. Picks a provider from config + environment.

If no provider can be configured, returns None so the agent can fall back to
rule-based (offline) operation on weak or disconnected devices.
"""

import os
from typing import Optional

from .anthropic_client import AnthropicClient
from .gemini_client import GeminiClient
from .groq_client import GroqClient
from .local_client import LocalClient
from .model_registry import ModelRegistry
from .openai_client import OpenAICompatibleClient


_PROVIDER_MAP = {
    "openai": OpenAICompatibleClient,
    "anthropic": AnthropicClient,
    "gemini": GeminiClient,
    "groq": GroqClient,
    "local": LocalClient,
}


def _env_for(provider: str) -> dict:
    if provider == "openai":
        return {"key": os.environ.get("OPENAI_API_KEY") or os.environ.get("GOAT_API_KEY")}
    if provider == "anthropic":
        return {"key": os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("CLAUDE_API_KEY")}
    if provider == "gemini":
        return {"key": os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")}
    if provider == "groq":
        return {"key": os.environ.get("GROQ_API_KEY")}
    if provider == "local":
        return {"key": os.environ.get("OLLAMA_API_KEY"), "url": os.environ.get("OLLAMA_BASE_URL")}
    return {}


def build_llm(
    provider: str = "auto",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    registry: Optional[ModelRegistry] = None,
    weak_device: bool = False,
) -> Optional[object]:
    registry = registry or ModelRegistry()
    provider = (provider or "auto").lower()

    if provider == "auto":
        provider = _auto_detect(registry)

    cls = _PROVIDER_MAP.get(provider)
    if cls is None:
        return None

    env_cfg = _env_for(provider)
    key = api_key or env_cfg.get("key") or _cfg_key(registry, provider)
    url = base_url or env_cfg.get("url") or registry.base_url(provider)
    resolved_model = registry.resolve(provider, model, weak_device)

    client = cls(api_key=key, base_url=url, model=resolved_model)
    if not client.is_configured():
        return None
    return client


def _cfg_key(registry: ModelRegistry, provider: str) -> Optional[str]:
    return (registry.providers.get(provider, {}) or {}).get("api_key")


def _auto_detect(registry: ModelRegistry) -> str:
    for provider, env_key in {
        "openai": ("OPENAI_API_KEY", "GOAT_API_KEY"),
        "anthropic": ("ANTHROPIC_API_KEY", "CLAUDE_API_KEY"),
        "gemini": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
        "groq": ("GROQ_API_KEY",),
    }.items():
        if any(os.environ.get(k) for k in env_key):
            return provider
    if os.environ.get("OLLAMA_BASE_URL") or _ollama_reachable():
        return "local"
    return registry.list_providers()[0] if registry.list_providers() else "openai"


def _ollama_reachable() -> bool:
    import urllib.request

    url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434") + "/api/tags"
    try:
        urllib.request.urlopen(url, timeout=1.5)
        return True
    except Exception:
        return False
