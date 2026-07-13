"""Telegram bot client (BotFather API) using only the standard library."""

import json
import os
import urllib.parse
import urllib.request


class TelegramClient:
    API = "https://api.telegram.org"

    def __init__(self, token: str):
        self.token = token
        self.base = f"{self.API}/bot{token}"

    def _get(self, method: str, params: dict):
        url = f"{self.base}/{method}?" + urllib.parse.urlencode(params)
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def get_updates(self, offset=None, timeout=30):
        params = {"timeout": timeout}
        if offset:
            params["offset"] = offset
        return self._get("getUpdates", params)

    def send_message(self, chat_id, text):
        return self._get(
            "sendMessage", {"chat_id": chat_id, "text": text[:4000], "parse_mode": "Markdown"}
        )
