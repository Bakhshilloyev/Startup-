#!/usr/bin/env bash
# Termux: run the agent as a long-lived REPL or one-shot task.
cd "$(dirname "$0")/../.."
export PYTHONPATH="$PWD/src:$PYTHONPATH"
export UNIFIED_WEAK_DEVICE=1
if [ -n "$1" ]; then
  python3 -m agent.cli "$@"
else
  python3 -m agent.cli --repl
fi
