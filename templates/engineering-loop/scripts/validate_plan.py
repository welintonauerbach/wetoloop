#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from loop_common import InvocationError, load_manifest

VALIDATORS = (
    "validate_manifest.py",
    "validate_prd.py",
    "validate_techspec.py",
    "validate_tasks.py",
    "validate_traceability.py",
    "validate_execution_state.py",
    "validate_lifecycle.py",
)

VALIDATOR_REQUIREMENTS = {
    "validate_prd.py": ("prd",),
    "validate_techspec.py": ("techspec",),
    "validate_tasks.py": ("tasks",),
    "validate_traceability.py": ("requirements", "tasks"),
}


def _selected_validators(plan: Path) -> tuple[list[str], list[str]]:
    manifest = load_manifest(plan)
    applicability = manifest.get("applicability") if isinstance(manifest.get("applicability"), dict) else {}
    applicable_values = {"required", "required_for_p0"}
    selected: list[str] = []
    skipped: list[str] = []
    for name in VALIDATORS:
        requirements = VALIDATOR_REQUIREMENTS.get(name, ())
        if requirements and not all(applicability.get(key) in applicable_values for key in requirements):
            skipped.append(name.removesuffix(".py"))
        else:
            selected.append(name)
    return selected, skipped


def _run(script_root: Path, name: str, plan: Path) -> tuple[int, dict[str, Any]]:
    completed = subprocess.run(
        [sys.executable, "-B", "-X", "utf8", str(script_root / name), "--plan", str(plan)],
        check=False,
        capture_output=True,
        encoding="utf-8",
        errors="strict",
        shell=False,
    )
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if len(lines) != 1:
        return 2, {"validator": name.removesuffix(".py"), "result": "ERROR", "error": "validator emitted a non-canonical output stream"}
    try:
        payload = json.loads(lines[0])
    except json.JSONDecodeError:
        return 2, {"validator": name.removesuffix(".py"), "result": "ERROR", "error": "validator output is not JSON"}
    if not isinstance(payload, dict) or completed.returncode not in {0, 1, 2, 3}:
        return 2, {"validator": name.removesuffix(".py"), "result": "ERROR", "error": "validator exit/output contract is invalid"}
    return completed.returncode, payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True, type=Path)
    args = parser.parse_args()
    plan = args.plan.resolve()
    script_root = Path(__file__).resolve().parent
    try:
        selected, skipped = _selected_validators(plan)
    except (InvocationError, OSError, ValueError) as exc:
        print(json.dumps({"validator": "validate_plan", "result": "ERROR", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    executions = [_run(script_root, name, plan) for name in selected]
    results = [payload for _, payload in executions]
    exit_codes = [code for code, _ in executions]
    if 3 in exit_codes:
        exit_code = 3
    elif 2 in exit_codes:
        exit_code = 2
    elif 1 in exit_codes:
        exit_code = 1
    else:
        exit_code = 0
    payload = {
        "validator": "validate_plan",
        "result": {0: "PASS", 1: "FAIL", 2: "ERROR", 3: "UNSAFE"}[exit_code],
        "validator_count": len(results),
        "skipped_validators": skipped,
        "validators": [
            {
                "name": result.get("validator"),
                "exit_code": code,
                "result": result.get("result"),
                "diagnostic_count": result.get("diagnostic_count", 0),
            }
            for (code, result) in executions
        ],
        "diagnostic_count": sum(int(result.get("diagnostic_count", 0)) for result in results),
        "diagnostics": [
            {"validator": result.get("validator"), **diagnostic}
            for result in results
            for diagnostic in result.get("diagnostics", [])
            if isinstance(diagnostic, dict)
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
