#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from common import markdown_table, print_errors, read, requirement_ids
from loop_checks import validate_traceability_contract
from loop_common import run_cli

def main() -> int:
    if "--plan" in sys.argv[1:]:
        parser = argparse.ArgumentParser()
        parser.add_argument("--plan", required=True, type=Path)
        args = parser.parse_args()
        return run_cli("validate_traceability", lambda: validate_traceability_contract(args.plan.resolve()))
    parser = argparse.ArgumentParser()
    parser.add_argument("--requirements", required=True)
    parser.add_argument("--techspec", required=True)
    parser.add_argument("--tasks", required=True)
    parser.add_argument("--task-dir", required=True)
    parser.add_argument("--validation")
    args = parser.parse_args()

    req_text = read(args.requirements)
    tech_text = read(args.techspec)
    task_index = read(args.tasks)
    errors: list[str] = []

    _, req_rows = markdown_table(req_text, "Requirement Catalog")
    req_ids = {
        rid
        for row in req_rows
        for rid in requirement_ids(row.get("Requirement ID", ""))
    }
    _, design_rows = markdown_table(tech_text, "Requirement-to-Design Mapping")
    design_ids = {
        rid for row in design_rows for rid in requirement_ids(row.get("Requirement ID", ""))
    }
    _, coverage_rows = markdown_table(task_index, "Requirement Coverage")
    task_ids = {
        rid for row in coverage_rows for rid in requirement_ids(row.get("Requirement ID", ""))
    }

    for rid in sorted(req_ids):
        if rid not in design_ids:
            errors.append(f"{rid}: missing design mapping")
        if rid not in task_ids:
            errors.append(f"{rid}: missing task mapping")

    if args.validation:
        validation_text = read(args.validation)
        _, evidence_rows = markdown_table(validation_text, "Requirement evidence")
        evidence_ids = {
            rid for row in evidence_rows for rid in requirement_ids(row.get("Requirement ID", ""))
        }
        for rid in sorted(req_ids - evidence_ids):
            errors.append(f"{rid}: missing validation evidence row")

    print(
        f"requirements={len(req_ids)} design={len(design_ids)} tasks={len(task_ids)}"
    )
    return print_errors(errors)

if __name__ == "__main__":
    raise SystemExit(main())
