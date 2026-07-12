"""LLM provider abstraction.

Goat speaks to language models through a small, unified interface. Three
backends are supported:

* ``openai``  - any OpenAI-compatible chat endpoint (OpenAI, OpenRouter,
  Mistral, together.ai, vLLM, Ollama, and Hermes-family local models).
* ``anthropic`` - the Anthropic Claude API (the "Claude Code" lineage).
* ``ollama``  - Ollama's OpenAI-compatible API, the default for weak devices
  and Termux because it runs fully offline on the local machine.

The agent always works with OpenAI style messages + tool schemas internally
and each backend converts as needed.
"""

import json
import os
import time
import urllib.error
import urllib.request

from . import platform as plat

TIMEOUT = 120


def _http(method: str, url: str, headers: dict, body: bytes = b""):
    """Minimal stdlib HTTP helper (no external dependency).

    Returns ``(status, text)`` for non-streaming use.
    """
    req = urllib.request.Request(url, data=body or None, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        return exc.code, detail
    except urllib.error.URLError as exc:
        return 0, f"{exc}"


def resolve_provider(name: str, api_key: str = "") -> str:
    """Resolve the ``auto`` provider into a concrete backend."""
    if name and name != "auto":
        return name
    key = api_key or os.environ.get("GOAT_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if key and key.startswith("sk-ant"):
        return "anthropic"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if key:
        return "openai"
    if _ollama_reachable():
        return "ollama"
    return "ollama"  # safest local default


def _ollama_reachable() -> bool:
    try:
        status, _ = _http("GET", "http://localhost:11434/api/tags", {}, b"")
        return status == 200
    except Exception:
        return False


class LLMProvider:
    """Base class. Subclasses implement :meth:`complete`."""

    name = "base"

    def __init__(self, cfg):
        self.cfg = cfg
        self.model = cfg.model()
        self.api_key = cfg.api_key()
        self.base_url = cfg.base_url()
        self.temperature = cfg.temperature()
        self.max_tokens = cfg.max_tokens()

    def complete(self, messages, tools, stream=False):
        """Return a dict ``{"content": str, "tool_calls": [...]}``.

        ``tool_calls`` entries are OpenAI-style dicts::

            {"id": str, "name": str, "arguments": str (json)}
        """
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, cfg):
        super().__init__(cfg)
        self.base_url = (self.base_url or "https://api.openai.com/v1").rstrip("/")
        if not self.model:
            self.model = os.environ.get("GOAT_MODEL") or "gpt-4o-mini"
        self.headers = {"Content-Type": "application/json"}
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"

    def complete(self, messages, tools, stream=True):
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": stream,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        url = f"{self.base_url}/chat/completions"
        if stream:
            return self._stream(url, payload)
        return self._oneshot(url, payload)

    def _oneshot(self, url, payload):
        status, text = _http(
            "POST", url, self.headers, json.dumps(payload).encode()
        )
        if status != 200:
            return {"content": f"[error {status}] {text}", "tool_calls": []}
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return {"content": f"[error] bad response: {text}", "tool_calls": []}
        msg = data["choices"][0]["message"]
        return {
            "content": msg.get("content") or "",
            "tool_calls": self._normalize_calls(msg.get("tool_calls")),
        }

    def _stream(self, url, payload):
        content = []
        calls = {}  # index -> {name, arguments}
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode(), method="POST", headers=self.headers
        )
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                for raw in resp:
                    line = raw.decode("utf-8", "replace").strip()
                    if not line or not line.startswith("data:"):
                        continue
                    data_str = line[len("data:") :].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
                    delta = chunk["choices"][0].get("delta", {})
                    if delta.get("content"):
                        content.append(delta["content"])
                    for tc in delta.get("tool_calls", []) or []:
                        idx = tc.get("index", 0)
                        slot = calls.setdefault(
                            idx, {"id": "", "name": "", "arguments": ""}
                        )
                        if tc.get("id"):
                            slot["id"] = tc["id"]
                        if tc.get("function"):
                            fn = tc["function"]
                            if fn.get("name"):
                                slot["name"] += fn["name"]
                            if fn.get("arguments"):
                                slot["arguments"] += fn["arguments"]
        except urllib.error.URLError as exc:
            return {"content": f"[error] {exc}", "tool_calls": []}
        except Exception as exc:  # pragma: no cover
            return {"content": f"[error] {exc}", "tool_calls": []}

        tool_calls = []
        for slot in calls.values():
            if slot["name"]:
                tool_calls.append(
                    {
                        "id": slot["id"] or f"call_{int(time.time())}",
                        "name": slot["name"],
                        "arguments": slot["arguments"] or "{}",
                    }
                )
        return {"content": "".join(content), "tool_calls": tool_calls}

    @staticmethod
    def _normalize_calls(raw):
        out = []
        for tc in raw or []:
            fn = tc.get("function", {})
            out.append(
                {
                    "id": tc.get("id", ""),
                    "name": fn.get("name", ""),
                    "arguments": fn.get("arguments", "{}"),
                }
            )
        return out


class OllamaProvider(OpenAIProvider):
    """Ollama exposes an OpenAI-compatible API locally (no API key)."""

    name = "ollama"

    def __init__(self, cfg):
        super().__init__(cfg)
        self.base_url = (self.base_url or "http://localhost:11434/v1").rstrip("/")
        if not self.model:
            self.model = os.environ.get("GOAT_MODEL") or "qwen2.5-coder:7b"
        # Strip any bearer header; Ollama does not need it.
        self.headers = {"Content-Type": "application/json"}


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, cfg):
        super().__init__(cfg)
        self.base_url = (self.base_url or "https://api.anthropic.com").rstrip("/")
        self.api_key = self.api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not self.model:
            self.model = os.environ.get("GOAT_MODEL") or "claude-3-5-sonnet-latest"
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }

    def complete(self, messages, tools, stream=False):
        sys_msgs = [m["content"] for m in messages if m["role"] == "system"]
        conv = [m for m in messages if m["role"] != "system"]
        anthropic_tools = []
        for t in tools:
            fn = t.get("function", {})
            anthropic_tools.append(
                {
                    "name": fn["name"],
                    "description": fn.get("description", ""),
                    "input_schema": fn.get("parameters", {}),
                }
            )
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": self._to_anthropic_messages(conv),
            "system": "\n\n".join(sys_msgs) if sys_msgs else None,
            "tools": anthropic_tools,
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        status, text = _http(
            "POST",
            f"{self.base_url}/v1/messages",
            self.headers,
            json.dumps(payload).encode(),
        )
        if status != 200:
            return {"content": f"[error {status}] {text}", "tool_calls": []}
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return {"content": f"[error] bad response: {text}", "tool_calls": []}

        content = []
        tool_calls = []
        for block in data.get("content", []):
            if block.get("type") == "text":
                content.append(block.get("text", ""))
            elif block.get("type") == "tool_use":
                tool_calls.append(
                    {
                        "id": block.get("id", ""),
                        "name": block.get("name", ""),
                        "arguments": json.dumps(block.get("input", {})),
                    }
                )
        return {"content": "".join(content), "tool_calls": tool_calls}

    @staticmethod
    def _to_anthropic_messages(conv):
        """Convert OpenAI-style messages incl. tool calls/results to Anthropic."""
        out = []
        for m in conv:
            role = m["role"]
            if role == "tool":
                last = out[-1] if out and out[-1]["role"] == "user" else None
                tool_result = {
                    "type": "tool_result",
                    "tool_use_id": m.get("tool_call_id", ""),
                    "content": m.get("content", ""),
                }
                if last is not None:
                    last["content"].append(tool_result)
                else:
                    out.append({"role": "user", "content": [tool_result]})
                continue

            if role == "assistant" and m.get("tool_calls"):
                blocks = []
                if m.get("content"):
                    blocks.append({"type": "text", "text": m["content"]})
                for tc in m["tool_calls"]:
                    try:
                        inp = json.loads(tc.get("arguments", "{}"))
                    except json.JSONDecodeError:
                        inp = {}
                    blocks.append(
                        {
                            "type": "tool_use",
                            "id": tc.get("id", ""),
                            "name": tc.get("name", ""),
                            "input": inp,
                        }
                    )
                out.append({"role": "assistant", "content": blocks})
                continue

            out.append({"role": role, "content": m.get("content", "")})
        return out


_PROVIDERS = {
    "openai": OpenAIProvider,
    "ollama": OllamaProvider,
    "anthropic": AnthropicProvider,
}


def get_provider(cfg) -> LLMProvider:
    name = resolve_provider(cfg.provider(), cfg.api_key())
    cls = _PROVIDERS.get(name, OllamaProvider)
    return cls(cfg)
