"""Discord / Slack webhook sender (incoming webhooks, stdlib only)."""

import json
import urllib.request


def send_webhook(url: str, text: str, username: str = "unified-agent"):
    payload = {"content": text, "username": username} if "discord" in url else {"text": text}
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status
