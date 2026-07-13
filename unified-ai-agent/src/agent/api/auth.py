"""API authentication: optional bearer-token gate."""

import hashlib
import hmac
import os


def check_token(provided: str | None) -> bool:
    expected = os.environ.get("UNIFIED_API_TOKEN")
    if not expected:
        return True
    if not provided:
        return False
    return hmac.compare_digest(provided, expected)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
