#!/usr/bin/env python3
"""Top-level runner. Adds src/ to the path so the agent runs without install.

Usage:
  python run.py "list files in the current directory"
  python run.py --repl
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from agent.cli import main

if __name__ == "__main__":
    sys.exit(main())
