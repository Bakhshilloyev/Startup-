"""Retry helper with exponential backoff for unreliable operations."""

import time
from typing import Callable, Type, Tuple


def retry(
    fn: Callable,
    attempts: int = 3,
    backoff: float = 1.0,
    exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    sleep: Callable[[float], None] = time.sleep,
):
    last = None
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except exceptions as exc:  # noqa: B902
            last = exc
            if attempt >= attempts:
                break
            sleep(backoff * (2 ** (attempt - 1)))
    raise last
