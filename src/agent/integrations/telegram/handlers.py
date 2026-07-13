"""Telegram message handling: routes messages and slash commands to the agent."""

from .bot import TelegramClient


def is_allowed(user_id, allowed: list) -> bool:
    if not allowed:
        return True
    return str(user_id) in [str(a) for a in allowed]


def handle_message(agent, client, update: dict, allowed: list):
    msg = update.get("message", {})
    chat_id = msg.get("chat", {}).get("id")
    text = (msg.get("text") or "").strip()
    user_id = msg.get("from", {}).get("id")
    if not text or not chat_id:
        return
    if not is_allowed(user_id, allowed):
        client.send_message(chat_id, "Unauthorized.")
        return
    if text.startswith("/"):
        reply = handle_command(agent, text)
    else:
        result = agent.run(text)
        v = result["verification"]
        reply = f"[{v['summary']}] {text}\n"
        if agent.offline:
            reply += "(offline mode)"
        else:
            reply += f"provider={agent.llm.name}"
    client.send_message(chat_id, reply)


def handle_command(agent, text: str) -> str:
    parts = text.split()
    cmd = parts[0].lower()
    if cmd in ("/start", "/help"):
        return "Goat Agent online. Send a task; use /reset, /model, /weak."
    if cmd == "/reset":
        agent.short_term.clear()
        return "Session reset."
    if cmd == "/model":
        return agent.llm.model if agent.llm else "offline"
    if cmd == "/weak":
        return f"weak_device = {getattr(agent, 'weak_device', False)}"
    return f"Unknown command: {cmd}"
