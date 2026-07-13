"""CPU architecture detection (32/64-bit, x86/arm and friends)."""

import platform
import struct


def bits() -> int:
    """Return the native pointer width: 32 or 64 (best effort)."""
    try:
        return struct.calcsize("P") * 8
    except Exception:
        return 64


def machine() -> str:
    """Return the raw machine string (e.g. x86_64, aarch64, armv7l)."""
    return platform.machine().lower()


def normalize_arch(raw: str | None = None) -> str:
    """Map a raw machine string to a normalized family name.

    Returns one of: x86, x64, armv7, arm64, aarch64, riscv, unknown.
    """
    m = (raw or machine()).lower()
    if m in ("x86_64", "amd64", "x64"):
        return "x64"
    if m in ("i386", "i686", "x86"):
        return "x86"
    if m in ("aarch64", "arm64"):
        return "aarch64" if bits() == 64 else "arm64"
    if m in ("armv7l", "armv7", "armv6l", "arm"):
        return "armv7"
    if m.startswith("riscv"):
        return "riscv"
    if m:
        return m
    return "unknown"


def is_64bit() -> bool:
    return bits() == 64


def is_arm() -> bool:
    fam = normalize_arch()
    return fam in ("armv7", "arm64", "aarch64")


def summary() -> dict:
    return {
        "bits": bits(),
        "machine": machine(),
        "arch": normalize_arch(),
        "is_64bit": is_64bit(),
        "is_arm": is_arm(),
        "python": platform.python_version(),
    }
