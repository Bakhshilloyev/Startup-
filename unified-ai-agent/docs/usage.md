# Usage

## Command line

```bash
# One-shot task (offline-capable)
python3 run.py "list files in the current directory"

# Interactive REPL
python3 run.py --repl

# Force a provider / model
python3 run.py --provider local --model qwen2.5-coder:7b "summarize this repo"

# Force weak-device mode
python3 run.py --weak "run: free -m"

# Machine-readable output
python3 run.py --json "fetch https://example.com"

# Point at a custom OpenAI-compatible endpoint
UNIFIED_BASE_URL=http://localhost:8080/v1 python3 run.py "..."
```

REPL commands: `/reset`, `/model`, `/weak`, `/exit`.

## HTTP API (optional)

```bash
export UNIFIED_API_TOKEN=secret
python3 -m agent.api
```

```bash
curl -H "Authorization: Bearer secret" http://127.0.0.1:8787/health
curl -H "Authorization: Bearer secret" -H "Content-Type: application/json" \
     -d '{"task":"list files"}' http://127.0.0.1:8787/run
```

## Telegram bot (optional)

```bash
export UNIFIED_TELEGRAM_TOKEN=123456:ABC...
python3 -m agent.integrations.telegram.commands
```

## Web UI (optional)

Serve `web/` over any static server (e.g. `python3 -m http.server` inside
`web/`) while the API runs, then open `index.html`.

## Programmatic

```python
from agent.app import create_agent
agent = create_agent(provider="local", model="qwen2.5-coder:7b")
result = agent.run("list files in the current directory")
print(result["verification"])
```
