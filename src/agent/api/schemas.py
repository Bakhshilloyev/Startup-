"""Request schemas and validation for the API."""


def validate_run(data: dict) -> dict:
    if not isinstance(data, dict):
        raise ValueError("body must be a JSON object")
    task = data.get("task")
    if not isinstance(task, str) or not task.strip():
        raise ValueError("'task' (non-empty string) is required")
    return {
        "task": task.strip(),
        "session_id": data.get("session_id"),
    }


def validate_health(_data: dict) -> dict:
    return {}
