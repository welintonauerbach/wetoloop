#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from common import (
    applicability_error,
    has_loop_version,
    is_meaningful,
    markdown_table,
    print_errors,
    read,
    require_headings,
    requirement_ids,
    section,
)
from loop_checks import validate_document
from loop_common import run_cli

def main() -> int:
    if "--plan" in sys.argv[1:]:
        parser = argparse.ArgumentParser()
        parser.add_argument("--plan", required=True, type=Path)
        args = parser.parse_args()
        return run_cli("validate_techspec", lambda: validate_document(args.plan.resolve(), "techspec"))
    parser = argparse.ArgumentParser()
    parser.add_argument("techspec")
    parser.add_argument("--requirements", required=True)
    args = parser.parse_args()

    text = read(args.techspec)
    req_text = read(args.requirements)
    errors: list[str] = []

    required_headings = [
        "Architecture Overview",
        "Reuse / Evolve / Create / Prohibited",
        "Risks & Concerns",
        "Requirement-to-Design Mapping",
        "Test Treatment",
        "Approved Deferrals",
    ]
    for heading in require_headings(text, required_headings):
        errors.append(f"missing required section: {heading}")

    _, req_rows = markdown_table(req_text, "Requirement Catalog")
    req_ids = {
        rid
        for row in req_rows
        for rid in requirement_ids(row.get("Requirement ID", ""))
    }
    _, mapping = markdown_table(text, "Requirement-to-Design Mapping")
    mapped = {rid for row in mapping for rid in requirement_ids(row.get("Requirement ID", ""))}
    for rid in sorted(req_ids - mapped):
        errors.append(f"{rid}: no TechSpec mapping")

    _, reuse_rows = markdown_table(text, "Reuse / Evolve / Create / Prohibited")
    allowed = {"REUSE", "EVOLVE", "CREATE", "PROHIBITED"}
    for index, row in enumerate(reuse_rows, start=1):
        decision = row.get("Decision", "").replace("`", "").strip()
        if decision not in allowed:
            errors.append(f"reuse row {index}: invalid Decision {decision!r}")
        if not requirement_ids(row.get("Requirement IDs", "")):
            errors.append(f"reuse row {index}: missing Requirement IDs")

    _, risks = markdown_table(text, "Risks & Concerns")
    if not risks:
        errors.append("Risks & Concerns table is empty")
    for index, row in enumerate(risks, start=1):
        for key in ("Concern", "Location (`file:line`)", "Impact", "Mitigation / task"):
            if not row.get(key, "").strip():
                errors.append(f"risk row {index}: empty {key}")

    treatment_headers, treatment = markdown_table(text, "Test Treatment")
    if not treatment:
        errors.append("Test Treatment table is empty")
    if has_loop_version(text):
        required_columns = {"Code layer", "Test type", "Risk/outcome proved", "Applicability", "Location pattern", "Gate"}
        for column in sorted(required_columns - set(treatment_headers)):
            errors.append(f"Test Treatment missing required column: {column}")
        for index, row in enumerate(treatment, start=1):
            issue = applicability_error(row.get("Applicability", ""))
            if issue:
                errors.append(f"Test Treatment row {index} Applicability {issue}")
            for column in ("Risk/outcome proved", "Location pattern", "Gate"):
                if not is_meaningful(row.get(column, "")):
                    errors.append(f"Test Treatment row {index}: empty or placeholder {column}")
        treatment_text = section(text, "Test Treatment")
        if "RunId" not in treatment_text or "producer" not in treatment_text.lower():
            errors.append("Test Treatment lacks RunId producer/reuse plan")

    for marker in ("TBD", "TODO", "<preencher>", "<fill>"):
        if marker.lower() in text.lower():
            errors.append(f"unresolved marker found: {marker}")

    print(f"requirements={len(req_ids)} mapped={len(mapped)}")
    return print_errors(errors)

if __name__ == "__main__":
    raise SystemExit(main())
