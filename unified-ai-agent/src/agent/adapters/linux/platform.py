"""Linux platform adapter."""

from .. import BasePlatform


class LinuxPlatform(BasePlatform):
    name = "linux"

    def open_path(self, path: str) -> str:
        return f"xdg-open '{path}' 2>/dev/null || true"

    def package_manager(self) -> str:
        import shutil

        if shutil.which("apt"):
            return "apt"
        if shutil.which("dnf"):
            return "dnf"
        if shutil.which("apk"):
            return "apk"
        if shutil.which("pacman"):
            return "pacman"
        return "pip"
