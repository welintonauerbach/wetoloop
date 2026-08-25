#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from common import markdown_table, print_errors, read, require_headings, requirement_ids
from loop_checks import validate_document
from loop_common import run_cli

PATTERNS = {"ALWAYS", "WHEN", "IF", "WHILE", "WHERE", "COMPLEX"}
DIMENSIONS = {
    "Input validation & bounds",
    "Failure / partial failure",
    "Idempotency / retry / duplicates",
    "Auth boundaries / rate limits",
    "Concurrency / ordering",
    "Data lifecycle / expiry",
    "Observability",
    "External dependency failure",
    "State-transition integrity",
}

def main() -> int:
    if "--plan" in sys.argv[1:]:
        parser = argparse.ArgumentParser()
        parser.add_argument("--plan", required=True, type=Path)
        args = parser.parse_args()
        return run_cli("validate_prd", lambda: validate_document(args.plan.resolve(), "prd"))
    parser = argparse.ArgumentParser()
    parser.add_argument("prd")
    parser.add_argument("--requirements")
    args = parser.parse_args()

    prd_text = read(args.prd)
    req_text = read(args.requirements) if args.requirements else prd_text
    errors: list[str] = []

    required = [
        "Problem Statement",
        "Goals",
        "Out of Scope",
        "Assumptions & Open Questions",
        "Implicit Requirement Closure",
        "Requirement Traceability",
        "Success Criteria",
    ]
    for heading in require_headings(prd_text if not args.requirements else req_text + "\n" + prd_text, required):
        errors.append(f"missing required section: {heading}")

    headers, rows = markdown_table(req_text, "Requirement Catalog")
    expected = {"Requirement ID", "Priority", "Pattern", "Requirement", "Source"}
    if not expected.issubset(set(headers)):
        errors.append(f"Requirement Catalog must contain columns: {sorted(expected)}")

    seen: set[str] = set()
    for index, row in enumerate(rows, start=1):
        rid_values = requirement_ids(row.get("Requirement ID", ""))
        if len(rid_values) != 1:
            errors.append(f"requirement row {index} has invalid Requirement ID")
            continue
        rid = rid_values[0]
        if rid in seen:
            errors.append(f"duplicate requirement ID: {rid}")
        seen.add(rid)
        pattern = row.get("Pattern", "").replace("`", "").strip().upper()
        if pattern not in PATTERNS:
            errors.append(f"{rid}: unsupported pattern {pattern!r}")
        statement = row.get("Requirement", "").replace("`", "").strip()
        if " SHALL " not in f" {statement} ":
            errors.append(f"{rid}: requirement must contain SHALL")
        if len(statement) < 25:
            errors.append(f"{rid}: requirement is too short to be precise")
        if not row.get("Priority", "").strip():
            errors.append(f"{rid}: Priority is empty")
        if not row.get("Source", "").strip():
            errors.append(f"{rid}: Source is empty")

    if not rows:
        errors.append("Requirement Catalog has no requirement rows")

    _, assumptions = markdown_table(req_text, "Assumptions & Open Questions")
    for index, row in enumerate(assumptions, start=1):
        for key in ("Ambiguity / decision", "Chosen default", "Rationale", "Confirmed?"):
            if not row.get(key, "").strip():
                errors.append(f"assumption row {index} has empty {key}")

    _, closure = markdown_table(req_text, "Implicit Requirement Closure")
    found_dimensions = {row.get("Dimension", "").strip() for row in closure}
    for dimension in sorted(DIMENSIONS - found_dimensions):
        errors.append(f"implicit requirement dimension missing: {dimension}")
    for row in closure:
        value = row.get("Requirement IDs or `N/A because`", "").strip()
        if not value:
            errors.append(f"closure row {row.get('Dimension','?')} is empty")
        elif not requirement_ids(value) and "N/A because" not in value:
            errors.append(
                f"closure row {row.get('Dimension','?')} must cite requirement IDs or N/A because"
            )

    _, trace = markdown_table(req_text, "Requirement Traceability")
    trace_ids = {rid for row in trace for rid in requirement_ids(row.get("Requirement ID", ""))}
    for rid in sorted(seen - trace_ids):
        errors.append(f"{rid}: missing from Requirement Traceability")

    open_markers = ("TBD", "TODO", "<preencher>", "<fill>")
    for marker in open_markers:
        if marker.lower() in req_text.lower():
            errors.append(f"unresolved marker found: {marker}")

    print(f"requirements={len(seen)}")
    return print_errors(errors)

if __name__ == "__main__":
    raise SystemExit(main())
