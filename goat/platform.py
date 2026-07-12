"""Platform detection for Linux, Windows, macOS and Termux.

Goat adapts its behaviour to the host. Termux on Android is treated as a
first-class target so the agent also runs well on weak devices.
"""

import os
import platform
import sys


def is_termux() -> bool:
    """Return True when running inside the Termux environment on Android."""
    if not sys.platform.startswith("linux"):
        return False
    # Termux exposes its prefix in environment variables and has a marker file.
    if os.environ.get("TERMUX_VERSION"):
        return True
    if os.environ.get("PREFIX") and "com.termux" in os.environ.get("PREFIX", ""):
        return True
    if os.path.exists("/data/data/com.termux/files/home"):
        return True
    return False


def detect() -> dict:
    """Detect the current platform and return a description dict."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if is_termux():
        name = "termux"
        family = "android"
        # Termux usually runs on ARM; weak-ish devices are common.
        weak = machine.startswith(("arm", "aarch"))
    elif system == "linux":
        name = "linux"
        family = "unix"
        weak = False
    elif system == "darwin":
        name = "macos"
        family = "unix"
        weak = False
    elif system == "windows":
        name = "windows"
        family = "windows"
        weak = False
    else:
        name = system or "unknown"
        family = "unknown"
        weak = False

    return {
        "name": name,
        "family": family,
        "machine": machine,
        "python": platform.python_version(),
        "weak_device": weak,
        "termux": name == "termux",
    }


def is_windows() -> bool:
    return detect()["family"] == "windows"


def shell_for_platform() -> str:
    """Return a sensible default shell for the current platform."""
    p = detect()
    if p["family"] == "windows":
        return os.environ.get("COMSPEC", "cmd.exe")
    if p["termux"] or p["family"] == "unix":
        return os.environ.get("SHELL", "/bin/bash")
    return "/bin/sh"
