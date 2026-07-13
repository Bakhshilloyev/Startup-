"""Slack webhook sender. Reuses the shared Discord/Slack webhook helper."""

from ..discord.webhook import send_webhook

__all__ = ["send_webhook"]
