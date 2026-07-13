"""Model registry: known providers, default models and weak-device fallbacks."""

from typing import Optional


class ModelRegistry:
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.providers = self.config.get("providers", {}) or {}
        self.weak = self.config.get("weak_device_models", {}) or {}

    def default_model(self, provider: str) -> Optional[str]:
        return self.providers.get(provider, {}).get("default_model")

    def base_url(self, provider: str) -> Optional[str]:
        return self.providers.get(provider, {}).get("base_url")

    def weak_model(self, provider: str) -> Optional[str]:
        return self.weak.get(provider)

    def resolve(self, provider: str, model: Optional[str], weak: bool = False):
        if weak and self.weak_model(provider):
            return self.weak_model(provider)
        return model or self.default_model(provider)

    def list_providers(self):
        return list(self.providers.keys())


DEFAULT_REGISTRY = {
    "providers": {
        "openai": {"default_model": "gpt-4o-mini", "base_url": "https://api.openai.com/v1"},
        "anthropic": {
            "default_model": "claude-3-5-haiku-latest",
            "base_url": "https://api.anthropic.com/v1",
        },
        "gemini": {
            "default_model": "gemini-1.5-flash",
            "base_url": "https://generativelanguage.googleapis.com/v1beta",
        },
        "groq": {"default_model": "llama-3.1-8b-instant", "base_url": "https://api.groq.com/openai/v1"},
        "local": {"default_model": "qwen2.5-coder:7b", "base_url": "http://localhost:11434/v1"},
    },
    "weak_device_models": {
        "local": "qwen2.5-coder:1.5b",
        "openai": "gpt-4o-mini",
        "groq": "llama-3.1-8b-instant",
    },
}
