"""Telegram bot integration (BotFather API), stdlib-only.

Connects Goat to Telegram so it can be driven from a chat. Uses long polling
against api.telegram.org and requires no third-party dependencies, keeping it
usable on weak devices and Termux.

Get a token from @BotFather, then either:

    export GOAT_TELEGRAM_TOKEN="123456:ABC..."
    goat --telegram

or set ``telegram_token`` in ~/.goat/config.toml.
"""

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

from . import config as cfgmod

API_BASE = "https://api.telegram.org/bot"
POLL_TIMEOUT = 30
HTTP_TIMEOUT = 60
MAX_MSG_LEN = 4096


def _api_call(token: str, method: str, params: dict = None, timeout: int = HTTP_TIMEOUT):
    url = f"{API_BASE}{token}/{method}"
    data = urllib.parse.urlencode(params or {}).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as exc:
        return {"ok": False, "error_code": exc.code, "description": exc.read().decode("utf-8", "replace")}
    except urllib.error.URLError as exc:
        return {"ok": False, "error_code": 0, "description": str(exc)}


class TelegramBot:
    def __init__(self, token: str, agent, ui=None, allowed: list = None):
        self.token = token
        self.agent = agent
        self.ui = ui
        self.allowed = set(str(a) for a in (allowed or []) if a)
        self.offset = 0
        self.commands = {
            "/start": self._cmd_start,
            "/help": self._cmd_help,
            "/reset": self._cmd_reset,
            "/model": self._cmd_model,
            "/key": self._cmd_key,
        }

    def _authorized(self, chat_id) -> bool:
        if not self.allowed:
            return True
        return str(chat_id) in self.allowed

    def get_me(self) -> bool:
        res = _api_call(self.token, "getMe")
        if res.get("ok"):
            self.ui and self.ui.info(
                f"Telegram bot @{res['result'].get('username')} connected."
            )
            return True
        self.ui and self.ui.error(f"Telegram getMe failed: {res}")
        return False

    def send(self, chat_id, text: str):
        """Send text, splitting into chunks if needed."""
        if not text:
            text = "(empty response)"
        chunks = [text[i : i + MAX_MSG_LEN] for i in range(0, len(text), MAX_MSG_LEN)]
        for chunk in chunks:
            _api_call(
                self.token,
                "sendMessage",
                {"chat_id": chat_id, "text": chunk, "disable_web_page_preview": "true"},
            )

    def _handle(self, chat_id, text: str):
        if text in self.commands:
            self.commands[text](chat_id)
            return
        if text.startswith("/model "):
            self.agent.provider.model = text[len("/model ") :].strip()
            self.send(chat_id, "model set to " + self.agent.provider.model)
            return
        if text.startswith("/provider "):
            from .llm import get_provider

            self.agent.provider = get_provider(self.agent.cfg)
            self.send(chat_id, "provider set to " + self.agent.provider.name)
            return
        if text.startswith("/key "):
            key = text[len("/key ") :].strip()
            if key:
                status = self.agent.set_api_key(key)
                self.send(
                    chat_id,
                    "api key set -> provider="
                    + status["provider"]
                    + " model="
                    + status["model"],
                )
            else:
                self.send(chat_id, "Send your key as: /key YOUR_API_KEY")
            return

        # Stream progress back to the chat as Goat works.
        def on_event(ev):
            if ev["type"] == "tool_call":
                self.send(chat_id, "🔧 " + ev["name"])

        self.send(chat_id, "⏳ thinking…")
        answer = self.agent.send(text, on_event=on_event)
        self.send(chat_id, answer)

    # --- slash commands --------------------------------------------------
    def _cmd_start(self, chat_id):
        self.send(
            chat_id,
            "🐐 Goat is online. Send me a coding task and I'll use my tools "
            "(read/write/edit files, run commands, search) to help.\n"
            "Commands: /help /reset /model /provider /key",
        )

    def _cmd_help(self, chat_id):
        self.send(
            chat_id,
            "Send any instruction as a message. Commands:\n"
            "/reset - clear conversation\n"
            "/model NAME - set model\n"
            "/provider NAME - openai|anthropic|ollama|auto\n"
            "/key KEY - set API key",
        )

    def _cmd_reset(self, chat_id):
        self.agent.reset()
        self.send(chat_id, "conversation reset.")

    def _cmd_model(self, chat_id):
        self.send(
            chat_id,
            "provider=" + self.agent.provider.name + " model=" + self.agent.provider.model,
        )

    def _cmd_key(self, chat_id):
        self.send(chat_id, "Send your key as: /key YOUR_API_KEY")

    # --- main loop -------------------------------------------------------
    def run(self):
        if not self.get_me():
            return 1
        self.ui and self.ui.info("Telegram polling started. Press Ctrl+C to stop.")
        while True:
            try:
                updates = _api_call(
                    self.token,
                    "getUpdates",
                    {
                        "offset": self.offset,
                        "timeout": POLL_TIMEOUT,
                        "allowed_updates": json.dumps(["message"]),
                    },
                )
                if not updates.get("ok"):
                    self.ui and self.ui.error(f"getUpdates: {updates}")
                    time.sleep(3)
                    continue
                for upd in updates.get("result", []):
                    self.offset = upd["update_id"] + 1
                    msg = upd.get("message")
                    if not msg:
                        continue
                    chat_id = msg["chat"]["id"]
                    text = (msg.get("text") or "").strip()
                    if not text:
                        continue
                    if not self._authorized(chat_id):
                        self.send(chat_id, "🚫 unauthorized")
                        continue
                    try:
                        self._handle(chat_id, text)
                    except Exception as exc:  # keep polling alive
                        self.ui and self.ui.error(f"handle error: {exc}")
                        self.send(chat_id, f"[error] {exc}")
            except KeyboardInterrupt:
                self.ui and self.ui.info("Telegram bot stopped.")
                break
            except Exception as exc:
                self.ui and self.ui.error(f"poll error: {exc}")
                time.sleep(3)
        return 0


def run_from_config(cfg, agent, ui) -> int:
    token = cfg.data.get("goat", {}).get("telegram_token") or os.environ.get(
        "GOAT_TELEGRAM_TOKEN", ""
    )
    if not token:
        ui.error(
            "No Telegram token. Set GOAT_TELEGRAM_TOKEN or telegram_token in config."
        )
        return 1
    allowed = cfg.data.get("goat", {}).get("telegram_allowed", "")
    allowed = [a.strip() for a in str(allowed).split(",") if a.strip()]
    bot = TelegramBot(token, agent, ui, allowed=allowed)
    return bot.run()
