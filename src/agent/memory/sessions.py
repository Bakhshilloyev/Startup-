"""Session persistence: save and load full agent sessions to disk."""

import json
import os
import time


class SessionManager:
    def __init__(self, sessions_dir: str = "data/memory/sessions"):
        self.dir = sessions_dir
        os.makedirs(self.dir, exist_ok=True)

    def save(self, session_id: str, payload: dict) -> str:
        path = os.path.join(self.dir, f"{session_id}.json")
        payload = dict(payload, saved_at=time.time())
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, default=str)
        return path

    def load(self, session_id: str):
        path = os.path.join(self.dir, f"{session_id}.json")
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    def list_sessions(self):
        return sorted(
            f[:-5] for f in os.listdir(self.dir) if f.endswith(".json")
        )
