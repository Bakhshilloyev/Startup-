"""Allow `python -m agent.api` to start the HTTP server."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ..runtime.bootstrap import build
from .server import run


def main():
    agent = build()
    host = os.environ.get("UNIFIED_API_HOST", "127.0.0.1")
    port = int(os.environ.get("UNIFIED_API_PORT", "8787"))
    run(agent, host=host, port=port)


if __name__ == "__main__":
    main()
