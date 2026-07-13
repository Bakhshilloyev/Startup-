"""Anthropic (Claude) provider client."""

from typing import Optional

from .provider_base import LLMProvider


class AnthropicClient(LLMProvider):
    name = "anthropic"
    API_VERSION = "2023-06-01"

    def chat(self, messages, tools=None, temperature=0.2, max_tokens=1024):
        url = f"{self.base_url}/messages"
        system = ""
        converted = []
        for m in messages:
            role = m.get("role")
            if role == "system":
                system = m.get("content", "")
                continue
            if role == "tool":
                converted.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": m.get("tool_call_id", "1"),
                                "content": m.get("content", ""),
                            }
                        ],
                    }
                )
                continue
            converted.append({"role": role, "content": m.get("content", "")})

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key or "",
            "anthropic-version": self.API_VERSION,
        }
        payload = {
            "model": self.model,
            "system": system,
            "messages": converted,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = [
                {
                    "name": t["function"]["name"],
                    "description": t["function"]["description"],
                    "input_schema": t["function"]["parameters"],
                }
                for t in tools
            ]
        resp = self._post(url, headers, payload)
        text = resp.get("content", [{}])[0].get("text", "")
        tool_calls = []
        for block in resp.get("content", []):
            if block.get("type") == "tool_use":
                tool_calls.append(
                    {
                        "id": block.get("id"),
                        "type": "function",
                        "function": {
                            "name": block.get("name"),
                            "arguments": json_dumps(block.get("input", {})),
                        },
                    }
                )
        return {"text": text, "tool_calls": tool_calls, "raw": resp}


def json_dumps(obj) -> str:
    import json

    return json.dumps(obj)
