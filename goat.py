#!/usr/bin/env python3
"""Convenience launcher: `python3 goat.py` or `./goat.py` from the repo root."""
import sys
from goat.cli import main

if __name__ == "__main__":
    sys.exit(main())
