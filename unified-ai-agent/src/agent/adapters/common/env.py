"""Environment and runtime capability detection."""

import os
import sys


def is_windows() -> bool:
    return os.name == "nt" or sys.platform.startswith("win")


def is_linux() -> bool:
    return sys.platform.startswith("linux")


def is_macos() -> bool:
    return sys.platform.startswith("darwin")


def is_termux() -> bool:
    """Detect the Termux terminal environment on Android."""
    if "TERMUX_VERSION" in os.environ:
        return True
    prefix = os.environ.get("PREFIX", "")
    return prefix.endswith("/com.termux/files/usr") or "/com.termux/" in prefix


def is_android() -> bool:
    return is_termux() or os.path.exists("/system/build.prop")


def has_gpu() -> bool:
    """Best-effort GPU detection; we never assume a GPU exists."""
    try:
        if is_windows():
            import subprocess

            out = subprocess.run(
                ["wmic", "path", "win32_VideoController", "get", "name"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return "Microsoft Basic Render" not in out.stdout and bool(out.stdout.strip())
        if os.path.exists("/proc/driver/nvidia"):
            return True
        import subprocess

        out = subprocess.run(
            ["lspci"], capture_output=True, text=True, timeout=5
        )
        return "VGA" in out.stdout or "3D controller" in out.stdout
    except Exception:
        return False


def has_docker() -> bool:
    try:
        import shutil

        if shutil.which("docker") is None:
            return False
        import subprocess

        r = subprocess.run(
            ["docker", "info"], capture_output=True, timeout=5
        )
        return r.returncode == 0
    except Exception:
        return False


def has_admin() -> bool:
    try:
        if is_windows():
            import ctypes

            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        return os.geteuid() == 0
    except Exception:
        return False


def terminal_features() -> dict:
    return {
        "color": sys.stdout.isatty() if hasattr(sys.stdout, "isatty") else False,
        "width": _term_width(),
        "unicode": sys.stdout.encoding and "utf" in sys.stdout.encoding.lower(),
    }


def _term_width() -> int:
    try:
        import shutil

        return shutil.get_terminal_size((80, 24)).columns
    except Exception:
        return 80


def platform_name() -> str:
    if is_termux():
        return "termux"
    if is_windows():
        return "windows"
    if is_macos():
        return "macos"
    if is_linux():
        return "linux"
    return "unknown"
