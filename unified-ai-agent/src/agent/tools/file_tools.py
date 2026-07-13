"""File system tools."""

import glob
import os
import re

from ..utils.files import safe_join
from ..utils.validators import validate_args


def _read_file(path, limit=None):
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    size = os.path.getsize(path)
    if limit is None and size > 5_000_000:
        limit = 5_000_000
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read() if limit is None else fh.read(limit)


def read_file(args):
    a = validate_args(
        {
            "path": {"type": "str", "required": True},
            "limit": {"type": "int", "required": False, "default": None},
        },
        args,
    )
    return _read_file(a["path"], a["limit"])


def write_file(args):
    a = validate_args(
        {
            "path": {"type": "str", "required": True},
            "content": {"type": "str", "required": True},
        },
        args,
    )
    os.makedirs(os.path.dirname(os.path.abspath(a["path"])), exist_ok=True)
    with open(a["path"], "w", encoding="utf-8") as fh:
        fh.write(a["content"])
    return {"written": a["path"], "bytes": len(a["content"].encode("utf-8"))}


def list_files(args):
    a = validate_args(
        {
            "path": {"type": "str", "required": False, "default": "."},
            "recursive": {"type": "bool", "required": False, "default": False},
        },
        args,
    )
    out = []
    if a["recursive"]:
        for root, dirs, files in os.walk(a["path"]):
            for name in files:
                out.append(os.path.join(root, name))
    else:
        for entry in sorted(os.listdir(a["path"])):
            out.append(entry)
    return {"entries": out, "count": len(out)}


def glob_files(args):
    a = validate_args(
        {"pattern": {"type": "str", "required": True}}, args
    )
    return {"matches": sorted(glob.glob(a["pattern"], recursive=True))}


def grep_files(args):
    a = validate_args(
        {
            "pattern": {"type": "str", "required": True},
            "path": {"type": "str", "required": False, "default": "."},
            "max": {"type": "int", "required": False, "default": 200},
        },
        args,
    )
    rx = re.compile(a["pattern"])
    results = []
    for root, _dirs, files in os.walk(a["path"]):
        for name in files:
            if len(results) >= a["max"]:
                break
            fp = os.path.join(root, name)
            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as fh:
                    for i, line in enumerate(fh, 1):
                        if rx.search(line):
                            results.append({"file": fp, "line": i, "text": line.rstrip("\n")})
                            if len(results) >= a["max"]:
                                break
            except Exception:
                continue
    return {"matches": results, "count": len(results)}


def edit_file(args):
    a = validate_args(
        {
            "path": {"type": "str", "required": True},
            "old_string": {"type": "str", "required": True},
            "new_string": {"type": "str", "required": True},
        },
        args,
    )
    text = _read_file(a["path"])
    if a["old_string"] not in text:
        raise ValueError("old_string not found in file")
    if text.count(a["old_string"]) > 1:
        raise ValueError("old_string is not unique; refine it")
    new = text.replace(a["old_string"], a["new_string"], 1)
    with open(a["path"], "w", encoding="utf-8") as fh:
        fh.write(new)
    return {"edited": a["path"]}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a text file's contents (optionally limited to N chars).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "limit": {"type": "integer"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create or overwrite a file with content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in a directory (recursively optional).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "recursive": {"type": "boolean"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "glob_files",
            "description": "Find files matching a glob pattern.",
            "parameters": {
                "type": "object",
                "properties": {"pattern": {"type": "string"}},
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep_files",
            "description": "Search file contents for a regex pattern.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                    "path": {"type": "string"},
                    "max": {"type": "integer"},
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Replace a unique substring in a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "old_string": {"type": "string"},
                    "new_string": {"type": "string"},
                },
                "required": ["path", "old_string", "new_string"],
            },
        },
    },
]

FN = {
    "read_file": read_file,
    "write_file": write_file,
    "list_files": list_files,
    "glob_files": glob_files,
    "grep_files": grep_files,
    "edit_file": edit_file,
}
