"""Tiny on-disk JSON cache with TTL for weak-device friendly result reuse."""

import json
import os
import time


class Cache:
    def __init__(self, path: str = "data/cache/cache.json", ttl: int = 3600):
        self.path = path
        self.ttl = ttl
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.data = self._load()

    def _load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return {}

    def _save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as fh:
                json.dump(self.data, fh)
        except Exception:
            pass

    def get(self, key: str):
        item = self.data.get(key)
        if not item:
            return None
        if time.time() - item.get("ts", 0) > self.ttl:
            self.data.pop(key, None)
            self._save()
            return None
        return item.get("value")

    def set(self, key: str, value) -> None:
        self.data[key] = {"value": value, "ts": time.time()}
        self._save()
