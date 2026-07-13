#!/usr/bin/env bash
# Termux / Android setup. Keep dependencies minimal.
set -e

pkg install -y python
python3 -m pip install --upgrade pip

# Core runs with NO extra packages. pyyaml is optional (we have a fallback).
python3 -m pip install -r requirements-termux.txt || true

echo "==> (Optional) on-device models via Ollama"
echo "    pkg install -y ollama && ollama pull qwen2.5-coder:1.5b"
echo "==> Done. Try:  python3 run.py \"list files in the current directory\""
