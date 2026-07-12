"""Terminal UI helpers.

Goat prefers ``rich`` for a polished experience, but degrades gracefully to
plain ``print`` when it is not installed so it keeps running on weak devices
and Termux installs with minimal dependencies.
"""

try:
    from rich.console import Console  # type: ignore
    from rich.markdown import Markdown  # type: ignore
    from rich.panel import Panel  # type: ignore
    from rich.syntax import Syntax  # type: ignore

    _RICH = True
except Exception:  # pragma: no cover
    _RICH = False

GOAT_ART = r"""
   ___________________________
  <  Goat - terminal AI agent >
   ---------------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
"""


class UI:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.console = Console() if _RICH else None

    def banner(self, platform_info: dict, provider: str, model: str):
        line = (
            f"Goat v0.1.0  |  {platform_info['name']} "
            f"({platform_info['machine']})"
            f"{'  [weak device]' if platform_info['weak_device'] else ''}"
            f"  |  provider: {provider}  model: {model}"
        )
        if _RICH:
            self.console.print(Panel(GOAT_ART, title="Goat", subtitle=line))
        else:
            print(GOAT_ART)
            print(line)
        print("Type 'help' for commands, 'exit' to quit.\n")

    def assistant(self, text: str):
        if not text:
            return
        if _RICH:
            self.console.print(Markdown(text))
        else:
            print(f"\nGoat: {text}\n")

    def assistant_stream(self, chunk: str):
        if _RICH:
            self.console.print(chunk, end="")
        else:
            print(chunk, end="", flush=True)

    def tool_call(self, name: str, arguments: str):
        if _RICH:
            self.console.print(f"[cyan]→ tool[/cyan] [bold]{name}[/bold] {arguments}")
        else:
            print(f"  -> tool: {name} {arguments}")

    def tool_result(self, result: str):
        preview = result if len(result) < 600 else result[:600] + "...[truncated]"
        if _RICH:
            self.console.print(f"[dim]{preview}[/dim]")
        else:
            print(f"  <- {preview}")

    def user_prompt(self) -> str:
        try:
            return input("you> ").strip()
        except EOFError:
            return "exit"

    def error(self, msg: str):
        if _RICH:
            self.console.print(f"[red]{msg}[/red]")
        else:
            print(f"error: {msg}")

    def info(self, msg: str):
        if _RICH:
            self.console.print(f"[yellow]{msg}[/yellow]")
        else:
            print(msg)

    def verbose_info(self, msg: str):
        if self.verbose:
            self.info(msg)
