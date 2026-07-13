"""Tool registry aggregator. Combines every tool module into one catalog."""

from . import api_tools, file_tools, memory_tools, shell_tools, web_tools

_MODULES = [file_tools, shell_tools, web_tools, api_tools, memory_tools]


def all_tools():
    tools = []
    for mod in _MODULES:
        tools.extend(getattr(mod, "TOOLS", []))
    return tools


def dispatch_table():
    table = {}
    for mod in _MODULES:
        table.update(getattr(mod, "FN", {}))
    return table


def names():
    return [t["function"]["name"] for t in all_tools()]


__all__ = ["all_tools", "dispatch_table", "names"]
