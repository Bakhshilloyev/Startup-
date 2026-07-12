"""Command line interface and REPL for Goat."""

import argparse
import os
import sys

from . import __version__, platform as plat
from . import config as cfgmod
from .agent import Agent
from .llm import resolve_provider
from .ui import UI


HELP_TEXT = """Goat commands (prefix with '/'):
  /help            show this help
  /reset           clear conversation history
  /model           show current provider and model
  /provider NAME   switch provider (openai|anthropic|ollama|auto)
  /model NAME      set model name
  /key KEY         set API key (saved to ~/.goat/config.toml)
  /cd PATH         change working directory
  /cwd             show working directory
  /exit, /quit     leave Goat

Anything else is sent to Goat as a normal instruction.
"""


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="goat",
        description="Goat - terminal AI coding agent (Hermes adaptability + "
        "Claude Code strength).",
    )
    p.add_argument("-v", "--version", action="version", version=f"goat {__version__}")
    p.add_argument("--provider", help="LLM provider: openai|anthropic|ollama|auto")
    p.add_argument("--model", help="model name")
    p.add_argument("--api-key", help="API key")
    p.add_argument("--base-url", help="custom API base URL")
    p.add_argument("--cwd", help="working directory", default=os.getcwd())
    p.add_argument("--config", help="path to config.toml")
    p.add_argument(
        "--telegram",
        action="store_true",
        help="run as a Telegram bot (needs GOAT_TELEGRAM_TOKEN or telegram_token)",
    )
    p.add_argument("--verbose", action="store_true", help="verbose logging")
    p.add_argument("task", nargs="*", help="optional one-shot task (non-interactive)")
    return p


def apply_cli_overrides(cfg, args) -> None:
    g = cfg.data.setdefault("goat", {})
    if args.provider:
        g["provider"] = args.provider
    if args.model:
        g["model"] = args.model
    if args.api_key:
        g["api_key"] = args.api_key
    if args.base_url:
        g["base_url"] = args.base_url
    if args.cwd:
        g["cwd"] = os.path.abspath(args.cwd)
    if args.verbose:
        g["verbose"] = True


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    cfg_path = (
        cfgmod.Path(args.config)
        if args.config
        else cfgmod.DEFAULT_CONFIG_FILE
    )
    cfg = cfgmod.load_config(cfg_path)
    apply_cli_overrides(cfg, args)

    pinfo = plat.detect()
    provider = resolve_provider(cfg.provider(), cfg.api_key())
    ui = UI(verbose=cfg.verbose())
    agent = Agent(cfg, ui=ui)

    if args.telegram:
        from .telegram import run_from_config

        return run_from_config(cfg, agent, ui)

    if args.task:
        task = " ".join(args.task)
        agent.send(task)
        return 0

    ui.banner(pinfo, provider, agent.provider.model)

    while True:
        try:
            line = ui.user_prompt()
        except KeyboardInterrupt:
            print()
            continue

        if not line:
            continue
        if line in ("exit", "quit", "/exit", "/quit"):
            print("bye.")
            break
        if line in ("help", "/help"):
            print(HELP_TEXT)
            continue
        if line == "/reset":
            agent.reset()
            ui.info("conversation reset.")
            continue
        if line == "/model":
            ui.info(f"provider={agent.provider.name} model={agent.provider.model}")
            continue
        if line.startswith("/key "):
            key = line[len("/key "):].strip()
            if not key:
                ui.info("usage: /key YOUR_API_KEY")
            else:
                status = agent.set_api_key(key)
                ui.info(
                    f"api key set -> provider={status['provider']} "
                    f"model={status['model']} saved={status['persisted']}"
                )
            continue
        if line == "/key":
            ui.info("usage: /key YOUR_API_KEY")
            continue
        if line == "/cwd":
            ui.info(agent.cwd)
            continue
        if line.startswith("/provider "):
            name = line[len("/provider ") :].strip()
            cfg.data["goat"]["provider"] = name
            from .llm import get_provider as _gp

            agent.provider = _gp(cfg)
            ui.info(f"provider set to {resolve_provider(cfg.provider(), cfg.api_key())}")
            continue
        if line.startswith("/model "):
            mdl = line[len("/model ") :].strip()
            cfg.data["goat"]["model"] = mdl
            agent.provider.model = mdl
            ui.info(f"model set to {mdl}")
            continue
        if line.startswith("/cd "):
            target = os.path.abspath(os.path.join(agent.cwd, line[len("/cd ") :].strip()))
            if os.path.isdir(target):
                agent.cwd = target
                cfg.data["goat"]["cwd"] = target
                ui.info(f"cwd -> {target}")
            else:
                ui.error(f"not a directory: {target}")
            continue

        agent.send(line)

    return 0


if __name__ == "__main__":
    sys.exit(main())
