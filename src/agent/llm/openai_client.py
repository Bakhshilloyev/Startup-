"""OpenAI-compatible chat completions client (also used by Groq and local/Ollama)."""

from typing import List, Optional

from .provider_base import LLMProvider


class OpenAICompatibleClient(LLMProvider):
    name = "openai-compatible"

    def __init__(self, api_key=None, base_url=None, model=None, timeout=60):
        super().__init__(api_key, base_url, model, timeout)
        if self.base_url and not self.base_url.rstrip("/").endswith("/v1"):
            self.base_url = self.base_url.rstrip("/") + "/v1"
        self.requires_key = True

    def is_configured(self) -> bool:
        if self.requires_key:
            return bool(self.api_key)
        return bool(self.base_url)

    def chat(self, messages, tools=None, temperature=0.2, max_tokens=1024):
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key or ''}",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        resp = self._post(url, headers, payload)
        return {
            "text": self._get_text(resp),
            "tool_calls": self._get_tool_calls(resp),
            "raw": resp,
        }
