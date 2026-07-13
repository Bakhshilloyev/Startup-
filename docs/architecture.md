# Architecture

The agent is a layered, modular system. Each layer is independently testable
and replaceable.

```
┌─────────────────────────────────────────────┐
│  CLI / API / Integrations (Telegram, etc.) │
├─────────────────────────────────────────────┤
│  core/  Agent → Planner → Executor →      │
│          Verifier, Tool Router, Safety       │
├─────────────────────────────────────────────┤
│  llm/   provider_base + openai/anthropic/ │
│          gemini/groq/local clients           │
├─────────────────────────────────────────────┤
│  tools/  file, shell, web, api, memory    │
├─────────────────────────────────────────────┤
│  memory/ short-term, long-term (SQLite)     │
├─────────────────────────────────────────────┤
│  adapters/ linux | windows | termux + common│
├─────────────────────────────────────────────┤
│  runtime/ bootstrap, dispatcher, cache, log │
└─────────────────────────────────────────────┘
```

## Data flow (one task)

1. `Agent.run(task)` builds a context (platform, session).
2. `Planner.plan()` produces ordered steps:
   - **LLM mode** — asks the model for a structured JSON plan.
   - **Rule mode** — deterministic intent detection (offline, weak devices).
3. `Executor` runs each step via the `Tool Router`, guarded by the
   `Policy Guard`.
4. `Verifier` checks that steps succeeded and the goal was met.
5. Results are stored in short-term (session) and long-term (SQLite) memory.

## Key design choices

- **Stdlib-first.** Core runs on Python 3.8+ with zero pip installs.
  `requests`/`rich`/`pyyaml` are optional accelerators with fallbacks.
- **Offline by default.** With no API key the agent still plans and executes
  using heuristics and local tools.
- **Weak-device aware.** `bootstrap.detect_weak_device()` switches to smaller
  models, disables heavy features, and keeps startup fast.
- **Safe.** `PolicyGuard` blocks destructive commands and gated actions.
