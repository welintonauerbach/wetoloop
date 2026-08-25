#!/usr/bin/env python3
"""Dependency-free WetoLoop Engineering Loop 0.0.1 parsing and CLI primitives."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable


class InvocationError(RuntimeError):
    """The command cannot safely inspect the requested input."""


class UnsafeMutationError(RuntimeError):
    """A mutation precondition is not satisfied."""


@dataclass(frozen=True, order=True)
class Diagnostic:
    code: str
    message: str
    path: str = ""

    def as_dict(self) -> dict[str, str]:
        result = {"code": self.code, "message": self.message}
        if self.path:
            result["path"] = self.path
        return result


def _scalar(value: str) -> Any:
    value = value.strip()
    if value.startswith(("|", ">")):
        raise InvocationError("block scalar syntax is outside the supported YAML subset")
    if re.search(r"(^|[\s:])(?:&|\*)[A-Za-z0-9_-]+", value) or value.startswith(("!", "<<")):
        raise InvocationError(f"anchors, aliases, tags and merge keys are forbidden: {value}")
    if " #" in value and not (value.startswith(('"', "'")) and value.endswith(value[0])):
        raise InvocationError("inline YAML comments are outside the supported subset")
    if value in {"null", "~"}:
        return None
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if value.startswith(("[", "{")):
        try:
            return json.loads(value)
        except json.JSONDecodeError as exc:
            raise InvocationError(f"unsupported inline YAML value: {value}") from exc
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_yaml_subset(text: str) -> dict[str, Any]:
    """Parse the deterministic mapping/list subset used by Loop manifests."""
    tokens: list[tuple[int, str, int]] = []
    for line_number, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if "\t" in raw[: len(raw) - len(raw.lstrip())]:
            raise InvocationError(f"tabs are forbidden in YAML indentation at line {line_number}")
        tokens.append((len(raw) - len(raw.lstrip(" ")), raw.strip(), line_number))

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
        if index >= len(tokens) or tokens[index][0] < indent:
            return {}, index
        is_list = tokens[index][1].startswith("- ")
        container: Any = [] if is_list else {}
        while index < len(tokens):
            current_indent, content, line_number = tokens[index]
            if current_indent < indent:
                break
            if current_indent > indent:
                raise InvocationError(f"unexpected indentation at line {line_number}")
            if is_list:
                if not content.startswith("- "):
                    break
                item = content[2:].strip()
                if not item:
                    value, index = parse_block(index + 1, indent + 2)
                    container.append(value)
                    continue
                if ":" in item:
                    key, raw_value = item.split(":", 1)
                    if key.strip() == "<<" or key.strip().startswith("!"):
                        raise InvocationError(f"merge keys and tags are forbidden at line {line_number}")
                    entry: dict[str, Any] = {key.strip(): _scalar(raw_value)} if raw_value.strip() else {}
                    index += 1
                    if index < len(tokens) and tokens[index][0] > indent:
                        nested, index = parse_block(index, tokens[index][0])
                        if raw_value.strip():
                            if not isinstance(nested, dict):
                                raise InvocationError(f"list mapping expected at line {line_number}")
                            duplicate_keys = set(entry).intersection(nested)
                            if duplicate_keys:
                                raise InvocationError(f"duplicate list mapping keys {sorted(duplicate_keys)} at line {line_number}")
                            entry.update(nested)
                        else:
                            entry[key.strip()] = nested
                    container.append(entry)
                    continue
                container.append(_scalar(item))
                index += 1
                continue

            if content.startswith("- ") or ":" not in content:
                raise InvocationError(f"mapping entry expected at line {line_number}")
            key, raw_value = content.split(":", 1)
            key = key.strip()
            if not key or key == "<<" or key.startswith("!") or key in container:
                raise InvocationError(f"empty or duplicate key at line {line_number}")
            index += 1
            if raw_value.strip():
                container[key] = _scalar(raw_value)
            elif index < len(tokens) and tokens[index][0] > indent:
                container[key], index = parse_block(index, tokens[index][0])
            else:
                container[key] = {}
        return container, index

    if not tokens:
        raise InvocationError("YAML document is empty")
    document, consumed = parse_block(0, tokens[0][0])
    if consumed != len(tokens) or not isinstance(document, dict):
        raise InvocationError("YAML root must be one mapping")
    return document


def read_utf8(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="strict")
    except (OSError, UnicodeError) as exc:
        raise InvocationError(f"cannot read UTF-8 file {path}: {exc}") from exc


def load_manifest(plan_root: Path) -> dict[str, Any]:
    manifest_path = plan_root / "PLAN.yaml"
    if not manifest_path.is_file():
        raise InvocationError(f"PLAN.yaml not found under {plan_root}")
    return parse_yaml_subset(read_utf8(manifest_path))


def parse_front_matter(path: Path) -> tuple[dict[str, Any], str]:
    text = read_utf8(path)
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n?", text, re.S)
    if not match:
        raise InvocationError(f"structured front matter missing in {path}")
    return parse_yaml_subset(match.group(1)), text[match.end() :]


def contained_relative_path(value: Any) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    normalized = value.replace("\\", "/")
    if normalized.startswith("/") or re.match(r"^[A-Za-z]:", normalized):
        return None
    if ".." in normalized.split("/") or "\\" in value:
        return None
    return normalized


def flatten_paths(artifacts: Any) -> list[str]:
    if not isinstance(artifacts, dict):
        return []
    result: list[str] = []
    for value in artifacts.values():
        values = value if isinstance(value, list) else [value]
        result.extend(item for item in values if isinstance(item, str))
    return result


def lifecycle_bucket(plan_root: Path) -> str | None:
    parent = plan_root.parent.name
    return {
        "_backlog": "backlog",
        "_in_progress": "in_progress",
        "_done": "done",
        "_cancelled": "cancelled",
        "_superseded": "superseded",
    }.get(parent)


def emit_result(validator: str, diagnostics: Iterable[Diagnostic]) -> int:
    ordered = sorted(set(diagnostics))
    payload = {
        "validator": validator,
        "result": "PASS" if not ordered else "FAIL",
        "diagnostic_count": len(ordered),
        "diagnostics": [item.as_dict() for item in ordered],
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if not ordered else 1


def run_cli(validator: str, action: Callable[[], Iterable[Diagnostic]]) -> int:
    try:
        return emit_result(validator, action())
    except UnsafeMutationError as exc:
        print(json.dumps({"validator": validator, "result": "UNSAFE", "error": str(exc)}, sort_keys=True))
        return 3
    except (InvocationError, OSError, ValueError) as exc:
        print(json.dumps({"validator": validator, "result": "ERROR", "error": str(exc)}, sort_keys=True))
        return 2
