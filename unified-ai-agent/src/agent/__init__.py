"""Unified cross-platform AI agent.

A compact but powerful operator that plans, executes, verifies and remembers.
The package is designed to run on Linux, Windows, Termux/Android and on
weak 32-bit devices with minimal dependencies (Python standard library only
for the core).
"""

from .version import __version__, __app_name__, __codename__

__all__ = ["__version__", "__app_name__", "__codename__"]
