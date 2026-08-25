#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from common import clean_code, has_loop_version, is_meaningful, markdown_table, print_errors, read, section
from loop_checks import validate_execution_state_contract
from loop_common import run_cli

SHA_RE = re.compile(r"\b[0-9a-f]{40}\b", re.I)

def parse_metadata(text: str) -> dict[str, str]:
    _, rows = markdown_table(text, "Metadata")
    result = {}
    for row in rows:
        field = row.get("Field") or row.get("Campo")
        value = row.get("Value") or row.get("Valor")
        if field:
            result[field.replace("`", "").strip()] = (value or "").strip()
    return result

def parse_report_fields(text: str) -> dict[str, str]:
    match = re.search(r"(?ms)^\|\s*Field\s*\|\s*Value\s*\|\s*$\n"
                      r"^\|[-\s|:]+\|\s*$\n(.*?)(?=^\s*$|^##|\Z)", text)
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 2:
            result[cells[0].replace("`", "").strip()] = cells[1].strip()
    return result

def parse_labeled_lines(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^([^:]+):\s*(.+?)\s*$", line.strip())
        if match:
            result[match.group(1).strip()] = clean_code(match.group(2))
    return result

def leading_int(value: str) -> int | None:
    match = re.match(r"^(\d+)\b", clean_code(value))
    return int(match.group(1)) if match else None

def percent(value: str) -> float | None:
    match = re.fullmatch(r"(\d+(?:[.,]\d+)?)%?", clean_code(value))
    return float(match.group(1).replace(",", ".")) if match else None

def main() -> int:
    if "--plan" in sys.argv[1:]:
        parser = argparse.ArgumentParser()
        parser.add_argument("--plan", required=True, type=Path)
        args = parser.parse_args()
        return run_cli("validate_execution_state", lambda: validate_execution_state_contract(args.plan.resolve()))
    parser = argparse.ArgumentParser()
    parser.add_argument("tasks_index")
    parser.add_argument("task_dir")
    parser.add_argument("--validation")
    args = parser.parse_args()

    errors: list[str] = []
    index_text = read(args.tasks_index)
    versioned_contract = has_loop_version(index_text)
    task_dir = Path(args.task_dir)
    task_files = sorted(task_dir.glob("task_*.md"))
    completed = 0

    for path in task_files:
        text = read(path)
        metadata = parse_metadata(text)
        status = metadata.get("Status", "").replace("`", "").strip().lower()
        if status == "completed":
            completed += 1
            result = text.split("## Result", 1)[-1]
            if "Focused verification: PASS" not in result:
                errors.append(f"{path.name}: completed without focused PASS")
            if "Review verdict: PASS" not in result:
                errors.append(f"{path.name}: completed without review PASS")
            if not SHA_RE.search(result):
                errors.append(f"{path.name}: completed without 40-char commit SHA")
            if "Evidence: PENDING" in result or "Evidence:" not in result:
                errors.append(f"{path.name}: completed without evidence path")
        elif status not in {"pending", "in_progress", "blocked", "waiting_for_fresh_verification"}:
            errors.append(f"{path.name}: invalid status {status!r}")

    if completed == len(task_files) and task_files:
        if not args.validation:
            errors.append("all tasks completed but --validation was not provided")
        else:
            validation = read(args.validation)
            if "VERDICT: PASS" not in validation and "| Verdict | `PASS` |" not in validation:
                errors.append("validation report verdict is not PASS")
            if not re.search(r"`[^`]+:\d+\s+[—-]\s+[^`]+`?", validation):
                errors.append("validation report lacks file:line assertion evidence")
            if versioned_contract:
                if not has_loop_version(validation):
                    errors.append("versioned task index requires a versioned validation report")
                fields = parse_report_fields(validation)
                for field in (
                    "Date",
                    "Requirements",
                    "Branch / HEAD",
                    "Base / diff",
                    "Run ID",
                    "Configuration",
                    "Environment",
                    "Verifier",
                    "Verdict",
                ):
                    if not is_meaningful(fields.get(field, "")):
                        errors.append(f"validation report missing required field {field}")

                _, requirement_evidence = markdown_table(validation, "Requirement evidence")
                if not requirement_evidence:
                    errors.append("Requirement evidence table is empty")
                for index, row in enumerate(requirement_evidence, start=1):
                    if clean_code(row.get("Result", "")).upper() != "PASS":
                        errors.append(f"Requirement evidence row {index}: Result must be PASS")

                package_gate = section(validation, "Package gate")
                for field in (
                    "Command(s):",
                    "Filter/scope:",
                    "Exit code:",
                    "Duration:",
                    "Unique test methods planned:",
                    "Discovered:",
                    "Executed:",
                    "Passed:",
                    "Failed:",
                    "Skipped + justification:",
                    "Timeouts:",
                    "Retries:",
                    "Flakes:",
                    "Warnings:",
                ):
                    if not re.search(rf"(?m)^{re.escape(field)}\s*\S+", package_gate):
                        errors.append(f"Package gate missing required evidence {field}")

                package_values = parse_labeled_lines(package_gate)
                numeric_fields = (
                    "Exit code",
                    "Unique test methods planned",
                    "Discovered",
                    "Executed",
                    "Passed",
                    "Failed",
                    "Skipped + justification",
                    "Timeouts",
                    "Retries",
                    "Flakes",
                    "Warnings",
                )
                numeric: dict[str, int] = {}
                for field in numeric_fields:
                    parsed = leading_int(package_values.get(field, ""))
                    if parsed is None:
                        errors.append(f"Package gate {field} must start with a non-negative integer")
                    else:
                        numeric[field] = parsed
                if numeric.get("Exit code") not in {None, 0}:
                    errors.append("Package gate Exit code must be 0")
                if numeric.get("Unique test methods planned") == 0:
                    errors.append("Package gate planned test methods must be non-zero")
                discovered = numeric.get("Discovered")
                executed = numeric.get("Executed")
                passed = numeric.get("Passed")
                failed = numeric.get("Failed")
                skipped = numeric.get("Skipped + justification")
                if discovered is not None and executed is not None and discovered != executed:
                    errors.append("Package gate discovered and executed counts differ")
                if None not in (executed, passed, failed, skipped) and passed + failed + skipped != executed:
                    errors.append("Package gate passed + failed + skipped does not equal executed")
                for field in ("Failed", "Timeouts", "Retries", "Flakes"):
                    if numeric.get(field) not in {None, 0}:
                        errors.append(f"Package gate {field} must be 0")
                skipped_text = package_values.get("Skipped + justification", "")
                if skipped and not re.search(r"\b(because|justif)", skipped_text, re.I):
                    errors.append("Package gate non-zero skips require an explicit justification")
                warnings = numeric.get("Warnings")
                warnings_text = package_values.get("Warnings", "")
                if warnings and not re.search(r"\b(evaluated|justif|accepted|known)\b", warnings_text, re.I):
                    errors.append("Package gate non-zero warnings require explicit evaluation")

                producer_headers, producer_rows = markdown_table(validation, "Producers and artifacts")
                for column in ("Producer", "Executions", "Reused by", "Artifact", "SHA-256 / identity", "Justification", "Result"):
                    if column not in producer_headers:
                        errors.append(f"Producers and artifacts missing required column: {column}")
                if not producer_rows:
                    errors.append("Producers and artifacts table is empty")
                repeated_producer = False
                for index, row in enumerate(producer_rows, start=1):
                    executions = leading_int(row.get("Executions", ""))
                    result = clean_code(row.get("Result", "")).upper()
                    justification = row.get("Justification", "")
                    if executions is None:
                        errors.append(f"Producer row {index}: Executions must be a non-negative integer")
                        continue
                    if executions == 0:
                        if result != "N/A" or not is_meaningful(justification):
                            errors.append(f"Producer row {index}: zero executions require N/A and justification")
                    else:
                        for column in ("Producer", "Reused by", "Artifact", "SHA-256 / identity"):
                            if not is_meaningful(row.get(column, "")):
                                errors.append(f"Producer row {index}: empty or placeholder {column}")
                        if result != "PASS":
                            errors.append(f"Producer row {index}: executed producer result must be PASS")
                    if executions > 1:
                        repeated_producer = True
                        if not is_meaningful(justification) or clean_code(justification).upper() in {"N/A", "NONE"}:
                            errors.append(f"Producer row {index}: repeated execution requires justification")

                coverage_headers, coverage_rows = markdown_table(validation, "Coverage")
                for column in ("Surface", "Covered / valid", "Total / valid", "Percent", "Threshold", "Result"):
                    if column not in coverage_headers:
                        errors.append(f"Coverage missing required column: {column}")
                if not coverage_rows:
                    errors.append("Coverage table is empty")
                coverage_has_pass = False
                for index, row in enumerate(coverage_rows, start=1):
                    result = clean_code(row.get("Result", "")).upper()
                    if result == "PASS":
                        coverage_has_pass = True
                        covered = leading_int(row.get("Covered / valid", ""))
                        total = leading_int(row.get("Total / valid", ""))
                        measured = percent(row.get("Percent", ""))
                        threshold = percent(row.get("Threshold", ""))
                        if None in (covered, total, measured, threshold) or total == 0 or covered > total:
                            errors.append(f"Coverage row {index}: invalid raw values")
                        else:
                            expected = covered * 100.0 / total
                            if abs(expected - measured) > 0.02:
                                errors.append(f"Coverage row {index}: percent does not match raw values")
                            if measured < threshold:
                                errors.append(f"Coverage row {index}: threshold not met")
                    elif result == "N/A":
                        if not re.fullmatch(r"N/A because\s+.+", clean_code(row.get("Threshold", "")), re.I):
                            errors.append(f"Coverage row {index}: N/A requires rationale in Threshold")
                    else:
                        errors.append(f"Coverage row {index}: Result must be PASS or N/A")

                sensor_text = section(validation, "Discrimination sensor")
                sensor_values = parse_labeled_lines(sensor_text)
                sensor_disposition = sensor_values.get("Disposition", "").upper()
                sensor_rationale = sensor_values.get("Risk and rationale", "")
                if sensor_disposition not in {"PASS", "NOT_REQUIRED"}:
                    errors.append("Discrimination sensor disposition must be PASS or NOT_REQUIRED")
                if not is_meaningful(sensor_rationale):
                    errors.append("Discrimination sensor requires a risk rationale")
                _, sensor_rows = markdown_table(validation, "Discrimination sensor")
                if sensor_disposition == "PASS":
                    if not sensor_rows:
                        errors.append("Discrimination sensor PASS requires mutation evidence")
                    for index, row in enumerate(sensor_rows, start=1):
                        if clean_code(row.get("Killed?", "")).upper() != "PASS":
                            errors.append(f"Discrimination sensor row {index}: mutation was not killed")

                final_rules = {
                    "DISCOVERY/EXECUTION RECONCILED": r"PASS",
                    "DUPLICATE PRODUCERS": r"NONE|JUSTIFIED",
                    "TIMEOUTS/RETRIES/FLAKES": r"NONE|RECONCILED",
                    "COVERAGE": r"PASS|N/A because\s+.+",
                    "DISCRIMINATION SENSOR": r"PASS|NOT_REQUIRED because\s+.+",
                    "PACKAGE GATE": r"PASS",
                }
                final_verdict = section(validation, "Final verdict")
                for field, allowed in final_rules.items():
                    if not re.search(rf"(?mi)^{re.escape(field)}:\s*(?:{allowed})\s*$", final_verdict):
                        errors.append(f"Final verdict has invalid or missing required field {field}")
                final_values = parse_labeled_lines(final_verdict)
                duplicate_result = final_values.get("DUPLICATE PRODUCERS", "").upper()
                if repeated_producer and duplicate_result != "JUSTIFIED":
                    errors.append("Final verdict must mark repeated producers as JUSTIFIED")
                if not repeated_producer and duplicate_result == "JUSTIFIED":
                    errors.append("Final verdict marks duplicate producers without repeated execution")
                coverage_result = final_values.get("COVERAGE", "")
                if coverage_has_pass and coverage_result.upper() != "PASS":
                    errors.append("Final verdict coverage contradicts measured PASS rows")
                if not coverage_has_pass and not re.fullmatch(r"N/A because\s+.+", coverage_result, re.I):
                    errors.append("Final verdict coverage requires N/A rationale when no row is measured")
                final_sensor = final_values.get("DISCRIMINATION SENSOR", "")
                final_sensor_disposition = re.split(r"\s+because\s+", final_sensor, maxsplit=1, flags=re.I)[0].strip().upper()
                if final_sensor_disposition != sensor_disposition:
                    errors.append("Final verdict discrimination sensor contradicts sensor evidence")

    print(f"tasks={len(task_files)} completed={completed}")
    return print_errors(errors)

if __name__ == "__main__":
    raise SystemExit(main())
