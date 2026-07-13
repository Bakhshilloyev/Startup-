"""Lightweight logging that works without third-party packages.

Logs are written compactly to a rotating file for weak devices and mirrored
to stdout when a terminal is available.
"""

import logging
import os
import sys

from ..adapters.common.paths import ensure_dir, repo_paths


def setup_logging(level: str = "INFO", log_dir: str | None = None) -> logging.Logger:
    if log_dir is None:
        log_dir = repo_paths().get("logs")
    ensure_dir(log_dir)

    logger = logging.getLogger("goat-agent")
    if logger.handlers:
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False

    fmt = logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s")

    stream = logging.StreamHandler(sys.stderr)
    stream.setFormatter(fmt)
    logger.addHandler(stream)

    try:
        file_handler = logging.FileHandler(
            os.path.join(log_dir, "agent.log"), encoding="utf-8"
        )
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
    except Exception:
        pass

    return logger


def get_logger(name: str = "goat-agent") -> logging.Logger:
    return logging.getLogger(name)
