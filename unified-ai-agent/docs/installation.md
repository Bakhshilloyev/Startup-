# Installation

The agent is clone-and-run. No build step is required for the core.

## 1. Clone

```bash
git clone https://github.com/your-org/unified-ai-agent.git
cd unified-ai-agent
```

## 2. Run (no install needed)

```bash
python3 run.py "list files in the current directory"
```

This works on Linux, Windows (PowerShell), macOS and Termux.

## 3. Optional: install as a command

```bash
python3 -m pip install -e .
unified-agent "explain this repository"
```

## 4. Optional dependencies

| Platform | File                         | Notes                        |
|----------|------------------------------|------------------------------|
| Linux    | `requirements-linux.txt`      | `pyyaml`, `requests`, `rich` |
| Windows  | `requirements-windows.txt`    | same                         |
| Termux   | `requirements-termux.txt`     | minimal; YAML fallback built in |

Platform helpers:

```bash
./scripts/setup.sh          # Linux / macOS
pwsh scripts/setup.ps1      # Windows
./scripts/setup_termux.sh   # Termux / Android
```

## 5. Choose a provider

Without any key the agent runs **offline** (rule-based). To use an LLM, set
one env var (see `.env.example`):

```bash
export OPENAI_API_KEY=sk-...
unified-agent "refactor utils.py to use pathlib"
```

Local/offline models via Ollama (great for Termux / weak devices):

```bash
ollama pull qwen2.5-coder:1.5b
export UNIFIED_PROVIDER=local
unified-agent "add a CLI flag to main.py"
```
