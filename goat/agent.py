"""The Goat agent loop.

Combines two lineages:

* **Hermes adaptability** - the system prompt is precise and instruction-led;
  the agent follows the user, uses tools when appropriate, and adapts its
  behaviour to context rather than rigidly following a script.
* **Claude Code strength** - it can read, write, and edit real files, run
  shell commands, and verify its own work. It reasons before acting and uses
  tools to confirm outcomes.
"""

from . import tools as toolmod
from .llm import get_provider
from .ui import UI

SYSTEM_PROMPT = """You are Goat, a terminal AI coding agent.

You combine two strengths:
- Hermes adaptability: you follow the user's instructions precisely, adapt to
  the project's context and conventions, and choose the right tool for the job.
- Claude Code strength: you can read, write, edit, search and run code on the
  real filesystem and shell, and you verify your work.

Operating principles:
1. Explore before you change. Use list_files, glob_files, grep_files and
   read_file to understand the codebase before editing.
2. Prefer small, surgical edits with edit_file. Use write_file to create new
   files. Never guess a file's content - read it first.
3. After changes, verify with run_command (tests, builds, linters) when
   available. Iterate until the task is correct.
4. Be concise. Explain what you are doing briefly, then act. Do not over-talk.
5. Respect the working directory and the user's environment. On weak devices
   (Termux/Android) keep operations light and avoid heavy toolchains.
6. If a tool fails, read the error, adapt, and retry. Do not give up silently.
7. You may use markdown in your replies, including fenced code blocks.

When the task is complete, give a short summary of what you did.
"""


class Agent:
    def __init__(self, cfg, ui: UI = None):
        self.cfg = cfg
        self.ui = ui or UI(verbose=cfg.verbose())
        self.provider = get_provider(cfg)
        self.cwd = cfg.cwd()
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.max_rounds = cfg.max_tool_rounds()

    def _call_model(self, stream: bool = True) -> dict:
        return self.provider.complete(self.messages, toolmod.TOOL_SCHEMAS, stream=stream)

    def send(self, user_text: str, on_event=None) -> str:
        """Run one user turn and return the final assistant text.

        If ``on_event`` is given it is called with dicts of the form
        ``{"type": "text"|"tool_call"|"tool_result", ...}`` so callers (e.g. the
        Telegram bot) can forward live progress to the user.
        """
        self.messages.append({"role": "user", "content": user_text})
        rounds = 0
        final_text = ""

        while rounds < self.max_rounds:
            rounds += 1
            result = self._call_model(stream=True)

            content = result.get("content", "")
            tool_calls = result.get("tool_calls", [])

            # Stream the assistant's spoken text to the user once.
            assistant_msg = {"role": "assistant", "content": content}
            if tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc.get("id", ""),
                        "name": tc.get("name", ""),
                        "arguments": tc.get("arguments", "{}"),
                    }
                    for tc in tool_calls
                ]
            self.messages.append(assistant_msg)

            if content:
                self.ui.assistant(content)
                if on_event:
                    on_event({"type": "text", "content": content})

            if not tool_calls:
                final_text = content
                break

            for tc in tool_calls:
                name = tc.get("name", "")
                args = tc.get("arguments", "{}")
                self.ui.tool_call(name, args)
                if on_event:
                    on_event({"type": "tool_call", "name": name, "arguments": args})
                output = toolmod.dispatch(name, args, self.cwd)
                self.ui.tool_result(output)
                if on_event:
                    on_event({"type": "tool_result", "name": name, "content": output})
                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.get("id", ""),
                        "name": name,
                        "content": output,
                    }
                )

        if rounds >= self.max_rounds and not final_text:
            final_text = (
                "[Goat stopped after the maximum number of tool rounds. "
                "You may continue the task with a follow-up message.]"
            )
            self.ui.error(final_text)

        return final_text

    def reset(self):
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    def set_api_key(self, key: str, persist: bool = True) -> dict:
        """Set the API key at runtime, re-resolve the provider, and persist.

        Returns a small status dict so callers (REPL / Telegram) can report it.
        """
        self.cfg.data["goat"]["api_key"] = key
        # With a key present, prefer a hosted provider over local Ollama.
        if self.cfg.provider() in ("auto", "ollama"):
            self.cfg.data["goat"]["provider"] = "auto"
        self.provider = get_provider(self.cfg)
        if persist:
            from . import config as cfgmod

            try:
                saved = cfgmod.save_config(self.cfg)
                persisted = str(saved)
            except Exception as exc:  # pragma: no cover - defensive
                persisted = f"(not saved: {exc})"
        else:
            persisted = "(not persisted)"
        return {
            "provider": self.provider.name,
            "model": self.provider.model,
            "persisted": persisted,
        }
