#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

REQ_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,15}-\d{3}\b")
COMMIT_RE = re.compile(
    r"^(feat|fix|docs|test|perf|refactor|chore|build|ci)"
    r"\([a-z0-9][a-z0-9-]*\): (task|cr)-\d{2} - .+"
)
LOOP_VERSION_RE = re.compile(
    r"^\|\s*Loop version\s*\|\s*`?\d+\.\d+(?:\.\d+)?`?\s*\|\s*$", re.M
)

def read(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")

def requirement_ids(text: str) -> list[str]:
    return REQ_RE.findall(text)

def has_loop_version(text: str) -> bool:
    return bool(LOOP_VERSION_RE.search(text))

def section(text: str, heading: str) -> str:
    pattern = re.compile(
        rf"(?ms)^##+\s+{re.escape(heading)}\s*$\n(.*?)(?=^##+\s+|\Z)"
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else ""

def markdown_table(text: str, heading: str) -> tuple[list[str], list[dict[str, str]]]:
    body = section(text, heading)
    lines = [line.strip() for line in body.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return [], []
    headers = [cell.strip() for cell in lines[0].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(headers):
            continue
        rows.append(dict(zip(headers, cells)))
    return headers, rows

def require_headings(text: str, headings: Iterable[str]) -> list[str]:
    return [heading for heading in headings if not section(text, heading)]

def print_errors(errors: list[str]) -> int:
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0

def clean_code(value: str) -> str:
    return value.replace("`", "").strip()

def is_meaningful(value: str) -> bool:
    cleaned = clean_code(value)
    return bool(cleaned) and not (cleaned.startswith("<") and cleaned.endswith(">"))

def applicability_error(value: str) -> str | None:
    cleaned = clean_code(value).strip()
    lowered = cleaned.lower()
    if lowered == "required":
        return None
    if re.fullmatch(r"n/a because\s+.+", cleaned, re.I):
        return None
    return "must be 'required' or 'N/A because <reason>'"

def split_ids(value: str) -> list[str]:
    return requirement_ids(value)

def task_id_from_path(path: Path) -> str | None:
    match = re.search(r"task_(\d{2})_", path.name)
    return match.group(1) if match else None
