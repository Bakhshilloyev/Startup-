"""Shared platform interface and detection factory."""

import os
import subprocess
from typing import Optional

from .common import arch, env, paths


class BasePlatform:
    name = "base"

    def shell_run(self, cmd, cwd=None, timeout=60, shell=True):
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }

    def pip_install(self, packages):
        return self.shell_run(
            [os.sys.executable, "-m", "pip", "install", *packages],
            shell=False,
        )

    def open_path(self, path: str) -> str:
        return f"echo 'open {path}'"

    def package_manager(self) -> str:
        return "pip"

    def data_dir(self) -> str:
        return paths.user_data_dir()

    def info(self) -> dict:
        return {
            "platform": self.name,
            "os": env.platform_name(),
            "arch": arch.summary(),
            "termux": env.is_termux(),
            "admin": env.has_admin(),
            "gpu": env.has_gpu(),
            "docker": env.has_docker(),
        }


def detect() -> BasePlatform:
    if env.is_termux():
        from .termux.platform import TermuxPlatform

        return TermuxPlatform()
    if env.is_windows():
        from .windows.platform import WindowsPlatform

        return WindowsPlatform()
    from .linux.platform import LinuxPlatform

    return LinuxPlatform()


__all__ = ["BasePlatform", "detect", "env", "arch", "paths"]
