# Troubleshooting

### "Mode: OFFLINE" and no real answers
No provider was configured. Set a key, e.g. `export OPENAI_API_KEY=sk-...`,
or use a local model (`GOAT_PROVIDER=local` + Ollama running).

### YAML config errors
Core ships a dependency-free YAML parser for simple configs. If you use
advanced YAML features, install `pyyaml` (`pip install pyyaml`).

### `PermissionError: shell execution is disabled`
`configs/permissions.yaml` has `allow_shell: false`, or the command matched a
blocked pattern in `blocked_commands`. Edit the config or avoid the command.

### Network tools fail on Termux
Termux may block background network. For local models, run Ollama inside
Termux and set `GOAT_BASE_URL=http://127.0.0.1:11434/v1`.

### Out of memory on a weak device
Force weak mode: `python3 run.py --weak ...`. This picks smaller models and
reduces concurrency/context.

### Import errors after moving files
Run from the repo root or set `PYTHONPATH=src`. The `run.py` launcher does
this for you.

### Tests
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```
