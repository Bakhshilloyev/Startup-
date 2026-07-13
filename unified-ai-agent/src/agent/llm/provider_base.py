"""Base class for LLM providers. Uses only the standard library for portability."""

import json
import urllib.error
import urllib.request
from typing import List, Optional

from ..runtime.errors import LLMError


class LLMProvider:
    name = "base"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 60,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.timeout = timeout

    def is_configured(self) -> bool:
        return bool(self.api_key or self.base_url)

    def chat(self, messages, tools=None, temperature=0.2, max_tokens=1024):
        raise NotImplementedError

    def _post(self, url: str, headers: dict, payload: dict) -> dict:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers=headers, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")
            raise LLMError(f"{self.name} HTTP {exc.code}: {body}", exc.code)
        except urllib.error.URLError as exc:
            raise LLMError(f"{self.name} connection error: {exc.reason}")
        except Exception as exc:  # noqa: B902
            raise LLMError(f"{self.name} request failed: {exc}")

    def _get_text(self, resp: dict) -> str:
        try:
            return resp["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError):
            return ""

    def _get_tool_calls(self, resp: dict) -> List[dict]:
        try:
            return resp["choices"][0]["message"].get("tool_calls") or []
        except (KeyError, IndexError, TypeError):
            return []
