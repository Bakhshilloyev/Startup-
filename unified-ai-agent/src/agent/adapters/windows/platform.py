"""Windows platform adapter."""

from .. import BasePlatform


class WindowsPlatform(BasePlatform):
    name = "windows"

    def shell_run(self, cmd, cwd=None, timeout=60, shell=True):
        import subprocess

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

    def open_path(self, path: str) -> str:
        return f'start "" "{path}"'

    def package_manager(self) -> str:
        return "pip"
