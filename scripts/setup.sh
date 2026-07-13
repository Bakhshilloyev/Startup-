#!/usr/bin/env bash
# Linux / macOS setup. Core is stdlib-only; extras are optional.
set -e

echo "==> Updating pip"
python3 -m pip install --upgrade pip

echo "==> Installing optional dependencies (skippable)"
python3 -m pip install -r requirements-linux.txt || echo "optional deps skipped"

echo "==> (Optional) install as a command"
python3 -m pip install -e . 2>/dev/null || echo "editable install skipped; use run.py"

echo "==> Done. Try:  python3 run.py \"list files in the current directory\""
