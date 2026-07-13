# Goat AI Agent

A **compact but powerful cross-platform AI operator** that plans, executes,
verifies and remembers. It runs on **Linux, Windows, Termux/Android and weak
32-bit devices** with the standard library only — no GPU, Docker, root, or
desktop environment required.

- 🧠 **Plans** tasks into small, ordered, executable steps.
- ⚙️ **Executes** via the safest compatible tool (files, shell, web, API, memory).
- ✅ **Verifies** results before reporting success.
- 💾 **Remembers** with short-term (session) and long-term (SQLite) memory.
- 🌍 **Cross-platform** — auto-detects OS, CPU arch (x86/x64/armv7/arm64),
  Python version and terminal features.
- 🪶 **Lightweight** — core is pure Python stdlib; `pyyaml`/`requests`/`rich`
  are optional accelerators with built-in fallbacks.
- 🔌 **Pluggable providers** — OpenAI, Anthropic, Gemini, Groq, and any
  OpenAI-compatible local model (Ollama/vLLM/LM Studio).
- 📴 **Offline by default** — with no API key it still runs via rule-based
  planning and local tools.

## Quick start

```bash
git clone https://github.com/your-org/goat-ai-agent.git
cd goat-ai-agent

# No install needed — core is stdlib-only:
python3 run.py "list files in the current directory"

# Or install as a command:
python3 -m pip install -e .
goat-agent "explain this repository"
```

Interactive REPL:

```bash
python3 run.py --repl
```

## Examples

```bash
# One-shot task (offline-capable)
python3 run.py "list files in the current directory"

# Use a local model (great for Termux / weak devices)
ollama pull qwen2.5-coder:1.5b
python3 run.py --provider local --model qwen2.5-coder:1.5b "add a CLI flag to main.py"

# Force weak-device mode (smaller models, reduced features)
python3 run.py --weak "run: free -m"

# Custom OpenAI-compatible endpoint
GOAT_BASE_URL=http://localhost:8080/v1 python3 run.py "..."
```

## Installation per platform

| Platform | Command |
|----------|----------|
| Linux / macOS | `./scripts/setup.sh` |
| Windows (PowerShell) | `pwsh scripts/setup.ps1` |
| Termux / Android | `./scripts/setup_termux.sh` |

See [`docs/installation.md`](docs/installation.md) for details.

## Architecture

```
CLI / API / Integrations
        │
core/   Agent → Planner → Executor → Verifier (+ Tool Router, Safety)
        │
llm/    provider_base + openai / anthropic / gemini / groq / local
        │
tools/   file, shell, web, api, memory
        │
memory/  short-term, long-term (SQLite)
        │
adapters/  linux | windows | termux + common (arch/env/paths)
        │
runtime/  bootstrap, dispatcher, cache, logging
```

See [`docs/architecture.md`](docs/architecture.md).

## Configuration

Configs live in `configs/` as simple YAML (`default`, `models`, `tools`,
`routes`, `permissions`). A dependency-free YAML parser is bundled, so
`pyyaml` is optional. Copy `.env.example` to `.env` to set providers/keys.

| File | Purpose |
|------|---------|
| `configs/default.yaml` | agent + runtime tuning |
| `configs/models.yaml` | providers, default & weak-device models |
| `configs/tools.yaml` | which tools are enabled |
| `configs/routes.yaml` | intent → tool mapping |
| `configs/permissions.yaml` | policy guard (blocked commands, gates) |

## Tools

`list_files` · `read_file` · `write_file` · `edit_file` · `glob_files` ·
`grep_files` · `run_command` · `fetch_url` · `http_request` · `remember` ·
`recall`

## HTTP API (optional)

```bash
export GOAT_API_TOKEN=secret
python3 -m agent.api
curl -H "Authorization: Bearer secret" http://127.0.0.1:8787/health
curl -H "Authorization: Bearer secret" -H "Content-Type: application/json" \
     -d '{"task":"list files"}' http://127.0.0.1:8787/run
```

## Tests

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

## Weak-device strategy

On Termux, 32-bit CPUs, or low-RAM machines the agent:

- picks smaller default models,
- keeps memory and startup low,
- disables unnecessary concurrency,
- prefers streaming and local tools,
- stores logs compactly.

Force it with `python3 run.py --weak ...` or `GOAT_WEAK_DEVICE=1`.

## Project layout

```
goat-ai-agent/
├── src/agent/        # all source (core, llm, tools, memory, adapters, api, …)
├── configs/          # YAML configuration
├── prompts/          # module prompts
├── tests/            # unittest suite
├── scripts/          # setup + utility scripts
├── docs/             # architecture, install, usage, troubleshooting, prompts
├── web/              # optional static UI
├── deployment/       # docker / systemd / windows / termux
├── data/             # memory / cache / logs (git-ignored)
├── run.py            # zero-install launcher
├── requirements*.txt
├── pyproject.toml
└── README.md
```

## License

MIT — see [`LICENSE`](LICENSE).
