"""Local model client (Ollama / vLLM / LM Studio via OpenAI-compatible API)."""

from typing import Optional

from .openai_client import OpenAICompatibleClient


class LocalClient(OpenAICompatibleClient):
    name = "local"

    def __init__(self, api_key=None, base_url=None, model=None, timeout=60):
        super().__init__(api_key, base_url, model, timeout)
        self.requires_key = False
