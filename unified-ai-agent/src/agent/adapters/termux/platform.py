"""Termux (Android) platform adapter with reduced-feature fallbacks."""

from .. import BasePlatform
from ..common import env


class TermuxPlatform(BasePlatform):
    name = "termux"

    def open_path(self, path: str) -> str:
        return f"termux-open '{path}' 2>/dev/null || true"

    def package_manager(self) -> str:
        return "pkg"

    def install_system_pkg(self, pkg: str) -> dict:
        return self.shell_run(f"pkg install -y {pkg}")

    def weak_device_default(self) -> bool:
        """Termux on phones is usually a constrained environment."""
        return True

    def info(self) -> dict:
        info = super().info()
        info["weak_device_default"] = self.weak_device_default()
        info["termux_api"] = env.is_termux()
        return info
