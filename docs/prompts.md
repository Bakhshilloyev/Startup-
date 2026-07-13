# Prompts

Prompts live in `prompts/` and are loaded as plain text. They are the
"personality" and role definitions for each module.

| File                  | Used by / role                              |
|-----------------------|---------------------------------------------|
| `system_prompt.txt`   | Root system prompt for the whole agent       |
| `planner_prompt.txt`  | Planner — task breakdown into steps          |
| `coder_prompt.txt`    | Coder — clean, portable code generation     |
| `researcher_prompt.txt`| Researcher — compare & summarize sources    |
| `tool_router_prompt.txt`| Tool Router — intent → tool selection     |
| `safety_prompt.txt`   | Policy Guard — block unsafe actions         |

## Customizing

Edit any `.txt` file directly. The CLI/agent loads them by path; to point the
agent at a custom set, place your versions under `configs/` or modify
`bootstrap` to load from your directory.

Keep prompts concise and deterministic. The agent favors reliability and
portability, so avoid prompts that assume a GPU, Docker, root, or a desktop
environment.
