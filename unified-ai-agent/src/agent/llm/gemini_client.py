"""Google Gemini provider client."""

from typing import Optional

from .provider_base import LLMProvider


class GeminiClient(LLMProvider):
    name = "gemini"

    def chat(self, messages, tools=None, temperature=0.2, max_tokens=1024):
        import json

        url = (
            f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key or ''}"
        )
        system = ""
        parts = []
        for m in messages:
            if m.get("role") == "system":
                system = m.get("content", "")
                continue
            parts.append({"text": f"{m.get('role')}: {m.get('content', '')}"})
        if system:
            parts.insert(0, {"text": f"[system] {system}"})

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        resp = self._post(url, headers, payload)
        text = (
            resp.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )
        return {"text": text, "tool_calls": [], "raw": resp}
