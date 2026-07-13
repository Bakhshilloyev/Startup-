# 🐐 Goat

**Goat** is a terminal AI coding agent that pairs **Hermes-style adaptability**
(precise instruction following + flexible tool use) with **Claude Code-style
strength** (real file reading, editing, and shell execution). It runs on
**Linux, Windows, macOS, and Termux** — including weak devices.

Goat is written in pure Python with minimal dependencies, so it installs
quickly and runs anywhere Python does, including Android's Termux.

## Features

- 🧠 **Adaptive** — follows your instructions, explores the codebase, and picks
  the right tool for the job.
- 💪 **Coding-strong** — reads, writes, edits, greases (globs/greps) and runs
  real shell commands, then verifies its own work.
- 🌍 **Cross-platform** — Linux, Windows, macOS and Termux. Defaults adapt to
  the device (lightweight models + Ollama on weak devices).
- 🔌 **Pluggable providers** — OpenAI, Anthropic (Claude), Ollama (local/offline),
  OpenRouter, Mistral, vLLM, and any OpenAI-compatible endpoint. Hermes-family
  local models work great via Ollama.
- 🪶 **Lightweight** — only `requests` required; `rich` is optional.

## Installation

### From GitHub (any platform)

```bash
git clone https://github.com/Bakhshilloyev/Startup-.git
cd Startup-
python3 goat.py          # no install needed; core is stdlib-only
# or install as a command:
pip install -e .
goat
```

### Linux / macOS / Termux

```bash
# optional but recommended: create a virtualenv
python3 -m venv .venv && source .venv/bin/activate

pip install -e .
# for the nicer UI:
pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

### Termux (Android)

```bash
pkg install python
pip install -e .
# for offline, on-device models:
pkg install ollama
ollama pull qwen2.5-coder:7b
```

## Quick start

```bash
# Interactive REPL
goat

# One-shot task
goat "refactor utils.py to use pathlib and run its tests"

# Use a specific provider / model
goat --provider anthropic --model claude-3-5-sonnet-latest "explain this repo"
goat --provider ollama --model qwen2.5-coder:7b "add a CLI flag to main.py"
```

## Configuration

Goat reads `~/.goat/config.toml`. Example:

```toml
[goat]
provider  = "auto"        # auto | openai | anthropic | ollama
model     = ""            # empty -> provider default
api_key   = ""            # or set GOAT_API_KEY / ANTHROPIC_API_KEY
base_url  = ""            # custom endpoint (OpenAI-compatible)
temperature = 0.2
max_tokens  = 2048
max_tool_rounds = 32
cwd = "."
```

Environment variables (`GOAT_PROVIDER`, `GOAT_MODEL`, `GOAT_API_KEY`,
`GOAT_BASE_URL`, …) override the file.

## REPL commands

| Command            | Description                          |
| ------------------ | ------------------------------------ |
| `/help`            | show help                           |
| `/reset`           | clear conversation history          |
| `/model`           | show provider + model               |
| `/provider NAME`   | switch provider                     |
| `/model NAME`      | set model                           |
| `/cd PATH`         | change working directory            |
| `/key KEY`         | set API key (saved to ~/.goat/config.toml) |
| `/endpoint URL`    | set custom endpoint (host:port)     |
| `/port PORT`       | set port on the endpoint            |
| `/version VER`     | set API version                     |
| `/cwd`             | print working directory             |
| `/exit`, `/quit`   | quit                                |

## Tools Goat can use

`read_file` · `write_file` · `edit_file` · `list_files` · `glob_files` ·
`grep_files` · `run_command`

## Custom endpoint, model, version and API key

Goat can point at any OpenAI-compatible server (vLLM, LM Studio, Ollama,
OpenRouter, Together, Azure, …) and use any model name. Configure via the
config file, environment variables, or live REPL / Telegram commands.

Config (`~/.goat/config.toml`):

```toml
provider   = "openai"
model      = "my-model"                 # any model name the endpoint serves
api_key    = "sk-..."                    # or GOAT_API_KEY
base_url   = "http://localhost:8080"     # host:port; /v1 is added automatically
api_version = ""                        # optional, sent as ?api-version= (Azure)
```

Live commands (REPL and Telegram):

```text
/key sk-...                 # set API key (persisted)
/endpoint http://host:8080  # custom endpoint with port
/port 8080                  # set port on the current endpoint
/version 2023-06-01         # set API version
/model my-model             # set model name
```

The endpoint URL may include the port. Goat appends `/v1/chat/completions`
automatically, and appends `?api-version=...` when `api_version` is set (useful
for Azure OpenAI). For Anthropic, `api_version` is sent as the
`anthropic-version` header.

## Telegram bot

Goat can also run as a Telegram bot (BotFather API), no extra dependencies:

1. Message [@BotFather](https://t.me/BotFather), create a bot, copy the token.
2. Set it (env takes precedence over config):

   ```bash
   export GOAT_TELEGRAM_TOKEN="123456:ABC..."
   goat --telegram
   ```

   or in `~/.goat/config.toml`:

   ```toml
   telegram_token = "123456:ABC..."
   telegram_allowed = ""   # comma-separated chat/user ids; empty = allow all
   ```

3. Open your bot in Telegram and send `/start`, then tasks. Goat streams
   progress (🔧 tool calls) and replies in chat. Slash commands `/reset`,
   `/model`, `/provider` work too.

The bot uses long polling against `api.telegram.org` and is fully stdlib-based,
so it also runs on Termux / weak devices.

## License

MIT
