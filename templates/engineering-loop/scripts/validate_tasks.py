#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from common import (
    COMMIT_RE,
    applicability_error,
    clean_code,
    has_loop_version,
    is_meaningful,
    markdown_table,
    print_errors,
    read,
    requirement_ids,
    section,
    task_id_from_path,
)
from loop_checks import validate_tasks_contract
from loop_common import run_cli

def parse_metadata(text: str) -> dict[str, str]:
    _, rows = markdown_table(text, "Metadata")
    result: dict[str, str] = {}
    for row in rows:
        if "Field" in row and "Value" in row:
            result[clean_code(row["Field"])] = row["Value"].strip()
        elif "Campo" in row and "Valor" in row:
            result[clean_code(row["Campo"])] = row["Valor"].strip()
    return result

def main() -> int:
    if "--plan" in sys.argv[1:]:
        parser = argparse.ArgumentParser()
        parser.add_argument("--plan", required=True, type=Path)
        args = parser.parse_args()
        return run_cli("validate_tasks", lambda: validate_tasks_contract(args.plan.resolve()))
    parser = argparse.ArgumentParser()
    parser.add_argument("tasks_index")
    parser.add_argument("task_dir")
    parser.add_argument("--requirements", required=True)
    args = parser.parse_args()

    index_text = read(args.tasks_index)
    req_text = read(args.requirements)
    _, req_rows = markdown_table(req_text, "Requirement Catalog")
    req_ids = {
        rid
        for row in req_rows
        for rid in requirement_ids(row.get("Requirement ID", ""))
    }
    task_dir = Path(args.task_dir)
    errors: list[str] = []
    versioned_contract = has_loop_version(index_text)

    required_index_sections = [
        "Test Coverage Matrix",
        "Gate Check Commands",
        "Phase Execution Map",
        "Task Index",
        "Dependency Cross-check",
        "Requirement Coverage",
    ]
    for heading in required_index_sections:
        if not markdown_table(index_text, heading)[1] and heading != "Phase Execution Map":
            errors.append(f"task index missing/empty section: {heading}")
        if heading == "Phase Execution Map" and f"## {heading}" not in index_text:
            errors.append(f"task index missing section: {heading}")

    if versioned_contract:
        coverage_headers, coverage_plan = markdown_table(index_text, "Test Coverage Matrix")
        for column in ("Code layer", "Test type", "Coverage expectation", "Applicability", "Location pattern", "Run command"):
            if column not in coverage_headers:
                errors.append(f"Test Coverage Matrix missing required column: {column}")
        for index, row in enumerate(coverage_plan, start=1):
            issue = applicability_error(row.get("Applicability", ""))
            if issue:
                errors.append(f"Test Coverage Matrix row {index} Applicability {issue}")
            for column in ("Coverage expectation", "Location pattern", "Run command"):
                if not is_meaningful(row.get(column, "")):
                    errors.append(f"Test Coverage Matrix row {index}: empty or placeholder {column}")

        gate_headers, gate_rows = markdown_table(index_text, "Gate Check Commands")
        for column in ("Gate", "When", "Command", "Producer/reuse plan", "Expected evidence"):
            if column not in gate_headers:
                errors.append(f"Gate Check Commands missing required column: {column}")
        for index, row in enumerate(gate_rows, start=1):
            for column in ("When", "Command", "Producer/reuse plan", "Expected evidence"):
                if not is_meaningful(row.get(column, "")):
                    errors.append(f"Gate Check Commands row {index}: empty or placeholder {column}")

    _, index_rows = markdown_table(index_text, "Task Index")
    tasks: dict[str, dict] = {}
    requirement_map: dict[str, set[str]] = {}

    for row in index_rows:
        task_cell = row.get("Task", "")
        link = re.search(r"\[(?:T)?(\d{2})\]\(([^)]+)\)", task_cell)
        if not link:
            errors.append(f"invalid Task link: {task_cell!r}")
            continue
        tid, rel_path = link.groups()
        path = Path(args.tasks_index).parent / rel_path
        if not path.exists():
            alt = task_dir / Path(rel_path).name
            path = alt
        if not path.exists():
            errors.append(f"T{tid}: task file not found: {rel_path}")
            continue
        text = read(path)
        metadata = parse_metadata(text)
        file_tid = task_id_from_path(path)
        if file_tid != tid:
            errors.append(f"T{tid}: task filename ID mismatch ({file_tid})")
        for field in ("Task ID", "Phase", "Status", "Requirements", "Depends on", "Tests", "Gate", "Commit"):
            if not metadata.get(field, "").strip():
                errors.append(f"T{tid}: missing metadata field {field}")
        for heading in ("What", "Where", "Reuses", "Done When", "TEST SCOPE", "Verification Gate", "Evidence Contract", "Result"):
            if f"## {heading}" not in text:
                errors.append(f"T{tid}: missing section {heading}")
        if versioned_contract:
            required_scope_fields = (
                "Projects affected:",
                "Production components changed:",
                "Test infrastructure changed:",
                "New/modified tests:",
                "Existing tests directly affected:",
                "Direct consumers:",
                "Special boundaries:",
                "Runtime/configuration relevant to the gate:",
                "Producer/reuse plan:",
                "Deferred package gates:",
                "Deferred ecosystem gates:",
                "Explicitly not authorized:",
            )
            scope_text = section(text, "TEST SCOPE")
            for field in required_scope_fields:
                if field not in scope_text:
                    errors.append(f"T{tid}: TEST SCOPE missing required field {field}")

            required_gate_fields = (
                "Commands:",
                "Expected assertions/outcomes:",
                "Expected unique methods/cases:",
                "Expected discovered/executed count or baseline:",
                "Applicability/N/A reasons:",
                "Timeout and retry policy:",
                "Evidence path:",
            )
            gate_text = section(text, "Verification Gate")
            for field in required_gate_fields:
                if field not in gate_text:
                    errors.append(f"T{tid}: Verification Gate missing required field {field}")

            evidence_text = section(text, "Evidence Contract")
            for field in (
                "Discovery/execution/results reconciled:",
                "Duplicate producers/retries/new skips:",
            ):
                if field not in evidence_text:
                    errors.append(f"T{tid}: Evidence Contract missing required field {field}")
        task_reqs = set(requirement_ids(metadata.get("Requirements", "")))
        if not task_reqs:
            errors.append(f"T{tid}: no Requirement IDs")
        unknown = task_reqs - req_ids
        for rid in sorted(unknown):
            errors.append(f"T{tid}: unknown requirement {rid}")
        for rid in task_reqs:
            requirement_map.setdefault(rid, set()).add(tid)
        commit = clean_code(metadata.get("Commit", ""))
        if commit and not COMMIT_RE.fullmatch(commit):
            errors.append(f"T{tid}: invalid conventional task commit: {commit!r}")
        depends = set(re.findall(r"\b\d{2}\b", metadata.get("Depends on", "")))
        if "None" in metadata.get("Depends on", ""):
            depends = set()
        phase_match = re.search(r"\d+", clean_code(metadata.get("Phase", "")))
        phase_num = int(phase_match.group()) if phase_match else 0
        tasks[tid] = {"depends": depends, "phase": phase_num, "path": path}

    for tid, task in tasks.items():
        for dep in task["depends"]:
            if dep not in tasks:
                errors.append(f"T{tid}: unknown dependency T{dep}")
            elif tasks[dep]["phase"] > task["phase"]:
                errors.append(f"T{tid}: forward-phase dependency on T{dep}")

    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(tid: str, stack: list[str]) -> None:
        if tid in visiting:
            errors.append("dependency cycle: " + " -> ".join(stack + [tid]))
            return
        if tid in visited:
            return
        visiting.add(tid)
        for dep in tasks.get(tid, {}).get("depends", set()):
            if dep in tasks:
                visit(dep, stack + [tid])
        visiting.remove(tid)
        visited.add(tid)
    for tid in tasks:
        visit(tid, [])

    for rid in sorted(req_ids - set(requirement_map)):
        errors.append(f"{rid}: not mapped to any task")

    _, coverage_rows = markdown_table(index_text, "Requirement Coverage")
    coverage_ids = {
        rid for row in coverage_rows for rid in requirement_ids(row.get("Requirement ID", ""))
    }
    for rid in sorted(req_ids - coverage_ids):
        errors.append(f"{rid}: absent from Requirement Coverage table")

    print(f"tasks={len(tasks)} requirements={len(req_ids)} mapped={len(requirement_map)}")
    return print_errors(errors)

if __name__ == "__main__":
    raise SystemExit(main())
