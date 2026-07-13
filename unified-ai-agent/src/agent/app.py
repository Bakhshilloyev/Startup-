"""Application factory and programmatic entry point.

Use this when embedding the agent or building an API/server on top of it.
"""

from .runtime.bootstrap import build


def create_agent(configs_dir=None, repo_root=None, **overrides):
    for key, value in overrides.items():
        import os

        os.environ[f"UNIFIED_{key.upper()}"] = str(value)
    return build(configs_dir=configs_dir, repo_root=repo_root)


__all__ = ["create_agent", "build"]
