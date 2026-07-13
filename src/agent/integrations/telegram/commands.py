"""Telegram command parsing helpers."""

from .handlers import handle_command
from .bot import TelegramClient


def run_bot(agent, token: str, allowed: list | None = None):
    client = TelegramClient(token)
    offset = None
    print("Telegram bot polling... (Ctrl+C to stop)")
    try:
        while True:
            updates = client.get_updates(offset=offset, timeout=30)
            for upd in updates.get("result", []):
                offset = upd["update_id"] + 1
                from .handlers import handle_message

                handle_message(agent, client, upd, allowed or [])
    except KeyboardInterrupt:
        pass
