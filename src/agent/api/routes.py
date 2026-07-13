"""Route handlers for the agent HTTP API."""

import json

from .auth import check_token
from .schemas import validate_run


def handle_health(agent, _body) -> dict:
    return {
        "status": "ok",
        "offline": agent.offline,
        "platform": agent.platform_info if hasattr(agent, "platform_info") else {},
        "weak_device": getattr(agent, "weak_device", False),
    }


def handle_run(agent, body) -> dict:
    req = validate_run(body)
    if req.get("session_id"):
        agent.set_session(req["session_id"])
    return agent.run(req["task"])


ROUTES = {
    "GET /health": (handle_health, None),
    "POST /run": (handle_run, {}),
}


def dispatch(agent, method: str, path: str, body: dict):
    key = f"{method} {path}"
    if key not in ROUTES:
        return 404, {"error": "not found"}
    handler, _schema = ROUTES[key]
    try:
        return 200, handler(agent, body or {})
    except ValueError as e:
        return 400, {"error": str(e)}
    except Exception as e:  # noqa: B902
        return 500, {"error": str(e)}
