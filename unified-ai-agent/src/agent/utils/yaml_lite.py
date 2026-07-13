"""Minimal YAML loader for the simple config subset used by this project.

We avoid a hard PyYAML dependency so the core runs on weak devices and Termux.
If PyYAML is installed it is used; otherwise this small parser handles nested
maps, block/flow sequences and scalars. The bundled configs stay within this
subset, so this fallback is sufficient and dependency-free.
"""

import json
from typing import Any

try:
    import yaml  # type: ignore

    _HAS_YAML = True
except Exception:  # pragma: no cover - optional dependency
    yaml = None
    _HAS_YAML = False


def load(text: str) -> Any:
    if _HAS_YAML:
        try:
            return yaml.safe_load(text)
        except Exception:
            pass
    return _parse(text)


def load_file(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return load(fh.read())


def _coerce(scalar: str) -> Any:
    s = scalar.strip()
    if s == "" or s.lower() in ("null", "~", "none"):
        return None
    if (s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'"):
        return s[1:-1]
    if s.lower() in ("true", "yes", "on"):
        return True
    if s.lower() in ("false", "no", "off"):
        return False
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s


def _strip_comment(line: str) -> str:
    out = []
    quote = None
    for ch in line:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
            out.append(ch)
        elif ch == "#":
            break
        else:
            out.append(ch)
    return "".join(out)


def _parse(text: str) -> Any:
    lines = []
    for raw in text.splitlines():
        stripped = _strip_comment(raw)
        if stripped.strip() == "":
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        lines.append((indent, stripped.strip()))

    value, _ = _parse_block(lines, 0, 0)
    return value if value is not None else {}


def _parse_block(lines: list, idx: int, indent: int):
    if idx >= len(lines):
        return None, idx

    cur_indent, cur = lines[idx]
    if cur_indent < indent:
        return None, idx

    if cur.startswith("- "):
        return _parse_sequence(lines, idx, cur_indent)
    return _parse_mapping(lines, idx, cur_indent)


def _parse_mapping(lines, idx, indent):
    result: dict = {}
    while idx < len(lines):
        cur_indent, cur = lines[idx]
        if cur_indent < indent:
            break
        if cur_indent > indent:
            break
        if cur.startswith("- "):
            break
        if ":" not in cur:
            idx += 1
            continue
        key, _, rest = cur.partition(":")
        key = key.strip()
        rest = rest.strip()
        if rest == "":
            child, idx = _parse_block(lines, idx + 1, indent + 1)
            result[key] = child if child is not None else {}
        else:
            result[key] = _parse_scalar_or_flow(rest)
            idx += 1
    return result, idx


def _parse_sequence(lines, idx, indent):
    result = []
    while idx < len(lines):
        cur_indent, cur = lines[idx]
        if cur_indent != indent or not cur.startswith("- "):
            if cur_indent < indent:
                break
            if cur_indent > indent:
                break
            if not cur.startswith("- "):
                break
        item = cur[2:].strip()
        if item == "":
            child, idx = _parse_block(lines, idx + 1, indent + 1)
            result.append(child)
        elif ":" in item and not item.startswith(("'", '"')):
            synth = [(indent + 2, item)]
            j = idx + 1
            while j < len(lines) and lines[j][0] > indent:
                synth.append(lines[j])
                j += 1
            sub, _ = _parse_mapping(synth, 0, indent + 2)
            result.append(sub)
            idx = j
        else:
            result.append(_parse_scalar_or_flow(item))
            idx += 1
    return result, idx


def _parse_scalar_or_flow(token: str) -> Any:
    token = token.strip()
    if token.startswith("[") and token.endswith("]"):
        inner = token[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar_or_flow(p) for p in _split_flow(inner)]
    if token.startswith("{") and token.endswith("}"):
        inner = token[1:-1].strip()
        obj = {}
        if inner:
            for part in _split_flow(inner):
                k, _, v = part.partition(":")
                obj[k.strip()] = _parse_scalar_or_flow(v.strip())
        return obj
    return _coerce(token)


def _split_flow(inner: str):
    parts = []
    depth = 0
    quote = None
    buf = []
    for ch in inner:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
            buf.append(ch)
        elif ch in "[{":
            depth += 1
            buf.append(ch)
        elif ch in "]}":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if buf:
        parts.append("".join(buf).strip())
    return [p for p in parts if p != ""]
