#!/usr/bin/env python3
"""Export the long-term memory store (SQLite) to a JSON file."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent.memory.sqlite_store import SQLiteStore


def main(argv=None):
    out = (argv or sys.argv[1:])
    out_path = out[0] if out else "data/memory/export.json"
    db_path = os.environ.get("GOAT_MEM_DB", "data/memory/agent.db")
    if not os.path.exists(db_path):
        print(f"No memory db at {db_path}")
        return 1
    store = SQLiteStore(db_path)
    rows = store.search("", limit=10_000)
    store.close()
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2)
    print(f"Exported {len(rows)} memories -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
