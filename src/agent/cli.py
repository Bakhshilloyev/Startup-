"""Command-line interface for the Goat AI Agent.

Usage:
  python -m agent.cli "list files in the current directory"
  python -m agent.cli --repl
  python -m agent.cli --provider ollama --model qwen2.5-coder:7b "summarize this repo"
"""

import argparse
import os
import sys

from .runtime.bootstrap import build
from .runtime.logging import setup_logging
from .version import __version__


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="goat-agent",
        description="Goat cross-platform AI agent (Linux, Windows, Termux).",
    )
    p.add_argument("task", nargs="*", help="Task to run (omit for REPL).")
    p.add_argument("--provider", help="LLM provider (openai|anthropic|gemini|groq|local|auto)")
    p.add_argument("--model", help="Model name (provider default if omitted).")
    p.add_argument("--api-key", help="API key (or set env GOAT_API_KEY).")
    p.add_argument("--base-url", help="Custom OpenAI-compatible base URL.")
    p.add_argument("--config-dir", help="Directory containing configs/*.yaml.")
    p.add_argument("--repo-root", help="Project root (defaults to cwd).")
    p.add_argument("--weak", action="store_true", help="Force weak-device mode.")
    p.add_argument("--repl", action="store_true", help="Start an interactive REPL.")
    p.add_argument("--json", action="store_true", help="Output raw JSON result.")
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--version", action="version", version=f"goat-agent {__version__}")
    return p


def _apply_cli_overrides(args, agent):
    if args.provider:
        os.environ["GOAT_PROVIDER"] = args.provider
    if args.model:
        os.environ["GOAT_MODEL"] = args.model
    if args.api_key:
        os.environ["GOAT_API_KEY"] = args.api_key
    if args.base_url:
        os.environ["GOAT_BASE_URL"] = args.base_url
    if args.weak:
        os.environ["GOAT_WEAK_DEVICE"] = "1"
    return agent


def run_once(agent, task: str, as_json: bool) -> int:
    result = agent.run(task)
    if as_json:
        import json

        print(json.dumps(result, indent=2, default=str))
    else:
        v = result["verification"]
        print(f"\nTask: {task}")
        print(f"Mode: {'OFFLINE' if agent.offline else 'LLM (' + (agent.llm.name if agent.llm else '?') + ')'}")
        print(f"Steps: {v['done']} done, {v['failed']} failed, {v['skipped']} skipped")
        print(f"Result: {v['summary']}")
        if agent.verbose:
            for s in result["steps"]:
                print(f"  - [{s['status']}] {s['description']}")
    return 0 if result["verification"]["ok"] else 1


def repl(agent):
    print(f"{agent.name} REPL (offline={agent.offline}). Type /exit to quit.")
    while True:
        try:
            task = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not task:
            continue
        if task in ("/exit", "/quit"):
            break
        if task == "/model":
            print(agent.llm.model if agent.llm else "offline")
            continue
        if task == "/weak":
            print("weak_device =", getattr(agent, "weak_device", False))
            continue
        run_once(agent, task, as_json=False)


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    setup_logging("DEBUG" if args.verbose else "INFO")
    agent = build(configs_dir=args.config_dir, repo_root=args.repo_root)
    agent.verbose = args.verbose
    _apply_cli_overrides(args, agent)
    if args.task:
        return run_once(agent, " ".join(args.task), as_json=args.json)
    if args.repl or not sys.stdin.isatty():
        return run_once(agent, input().strip(), as_json=args.json)
    repl(agent)
    return 0


if __name__ == "__main__":
    sys.exit(main())
