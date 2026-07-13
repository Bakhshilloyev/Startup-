"""Long-term memory backed by the SQLite store."""

from .sqlite_store import SQLiteStore


class LongTermMemory:
    def __init__(self, store: SQLiteStore = None, path: str = "data/memory/agent.db"):
        self.store = store or SQLiteStore(path)

    def remember(self, key: str, value: str) -> None:
        self.store.put(key, value)

    def recall(self, key: str) -> str:
        return self.store.get(key)

    def search(self, query: str, limit: int = 20):
        return self.store.search(query, limit)

    def forget(self, key: str) -> None:
        self.store.delete(key)

    def close(self):
        self.store.close()
