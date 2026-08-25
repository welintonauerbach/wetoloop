#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from loop_common import (
    Diagnostic,
    contained_relative_path,
    flatten_paths,
    lifecycle_bucket,
    load_manifest,
    run_cli,
)

EXPECTED_GROUPS = (
    ("definition", 1, "01-definition"),
    ("design", 2, "02-design"),
    ("execution", 3, "03-execution"),
    ("validation", 4, "04-validation"),
    ("governance", 5, "05-governance"),
)

TIER_REQUIRED = {
    "S": {"state"},
    "M": {"context", "requirements", "prd", "techspec", "tasks", "test_strategy", "state", "validation_report"},
    "L": {"context", "recon", "requirements", "prd", "decisions", "contracts", "techspec", "tasks", "test_strategy", "execution_prompt", "review_loop", "corrective_loop", "state", "validation_report", "independent_verifier", "learnings"},
    "X": {"context", "recon", "requirements", "prd", "decisions", "contracts", "techspec", "tasks", "test_strategy", "execution_prompt", "review_loop", "corrective_loop", "state", "validation_report", "independent_verifier", "learnings"},
}

APPLICABILITY_ARTIFACTS = {
    "context": ("context",),
    "recon": ("recon",),
    "requirements": ("requirements",),
    "prd": ("prd",),
    "decisions": ("decisions",),
    "contracts": ("contracts",),
    "techspec": ("techspec",),
    "readiness": ("readiness",),
    "tasks": ("tasks_index", "tasks_directory"),
    "test_strategy": ("test_strategy",),
    "execution_prompt": ("execution_prompt",),
    "review_loop": ("review_loop",),
    "corrective_loop": ("corrective_loop",),
    "state": ("state",),
    "validation_report": ("validation_report",),
    "independent_verifier": ("approval_record",),
    "learnings": ("learnings",),
    "discrimination_sensor": ("test_strategy",),
}

ARTIFACT_APPLICABILITY = {
    "adrs_directory": "decisions",
    "readiness": "readiness",
    "tasks_index": "tasks",
    "tasks_directory": "tasks",
    "evidence_directory": "validation_report",
    "harness": "readiness",
    "approval_record": "independent_verifier",
}


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _schema_type(value: Any, expected: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }.get(expected, False)


def _schema_diagnostics(value: Any, schema: dict[str, Any], root: dict[str, Any], path: str = "$") -> list[str]:
    if "$ref" in schema:
        reference = schema["$ref"]
        if not isinstance(reference, str) or not reference.startswith("#/"):
            return [f"{path}: unsupported schema reference {reference!r}"]
        target: Any = root
        for part in reference[2:].split("/"):
            if not isinstance(target, dict) or part not in target:
                return [f"{path}: unresolved schema reference {reference}"]
            target = target[part]
        return _schema_diagnostics(value, target, root, path)

    errors: list[str] = []
    for branch in schema.get("allOf", []):
        errors.extend(_schema_diagnostics(value, branch, root, path))
    if "oneOf" in schema:
        matches = sum(not _schema_diagnostics(value, branch, root, path) for branch in schema["oneOf"])
        if matches != 1:
            errors.append(f"{path}: expected exactly one oneOf branch, found {matches}")
        return errors

    expected = schema.get("type")
    expected_types = expected if isinstance(expected, list) else [expected] if isinstance(expected, str) else []
    if expected_types and not any(_schema_type(value, item) for item in expected_types):
        errors.append(f"{path}: expected type {expected_types}, found {type(value).__name__}")
        return errors
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected constant {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value {value!r} is outside enum")

    if isinstance(value, str):
        if len(value) < int(schema.get("minLength", 0)):
            errors.append(f"{path}: string is shorter than minLength")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.search(pattern, value) is None:
            errors.append(f"{path}: string does not match schema pattern")
    elif isinstance(value, dict):
        if len(value) < int(schema.get("minProperties", 0)):
            errors.append(f"{path}: object has too few properties")
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: required property {key!r} is missing")
        properties = schema.get("properties") if isinstance(schema.get("properties"), dict) else {}
        for key, item in value.items():
            child_path = f"{path}.{key}"
            if key in properties:
                errors.extend(_schema_diagnostics(item, properties[key], root, child_path))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{child_path}: additional property is forbidden")
            elif isinstance(schema.get("additionalProperties"), dict):
                errors.extend(_schema_diagnostics(item, schema["additionalProperties"], root, child_path))
    elif isinstance(value, list):
        if len(value) < int(schema.get("minItems", 0)):
            errors.append(f"{path}: array has too few items")
        if "maxItems" in schema and len(value) > int(schema["maxItems"]):
            errors.append(f"{path}: array has too many items")
        if schema.get("uniqueItems"):
            canonical = [json.dumps(item, ensure_ascii=False, sort_keys=True) for item in value]
            if len(canonical) != len(set(canonical)):
                errors.append(f"{path}: array items must be unique")
        prefix = schema.get("prefixItems") if isinstance(schema.get("prefixItems"), list) else []
        for index, item in enumerate(value):
            if index < len(prefix):
                errors.extend(_schema_diagnostics(item, prefix[index], root, f"{path}[{index}]"))
            elif schema.get("items") is False:
                errors.append(f"{path}[{index}]: additional array item is forbidden")
            elif isinstance(schema.get("items"), dict):
                errors.extend(_schema_diagnostics(item, schema["items"], root, f"{path}[{index}]"))
    return errors


def validate(plan_root: Path) -> list[Diagnostic]:
    manifest = load_manifest(plan_root)
    errors: list[Diagnostic] = []
    if manifest.get("schema_version") != 1 or manifest.get("loop_version") != "0.0.1":
        errors.append(Diagnostic("MANIFEST_VERSION", "schema_version=1 and loop_version=0.0.1 are required", "PLAN.yaml"))

    schema_path = Path(__file__).resolve().parents[1] / "schemas" / "plan.schema.json"
    if not schema_path.is_file():
        errors.append(Diagnostic("SCHEMA_MISSING", "canonical plan schema is required", str(schema_path)))
    else:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        if schema.get("$id") != "https://github.com/welintonauerbach/wetoloop/schemas/engineering-loop/v0.0.1/plan.schema.json":
            errors.append(Diagnostic("SCHEMA_ID", "plan schema identity is not canonical", str(schema_path)))
        for message in _schema_diagnostics(manifest, schema, schema):
            errors.append(Diagnostic("SCHEMA_VALIDATION", message, "PLAN.yaml"))

    plan = _mapping(manifest.get("plan"))
    tier = plan.get("tier")
    if tier not in TIER_REQUIRED:
        errors.append(Diagnostic("TIER_UNKNOWN", "plan.tier must be S, M, L or X", "PLAN.yaml"))
    bucket = lifecycle_bucket(plan_root)
    if bucket is None:
        errors.append(Diagnostic("BUCKET_UNKNOWN", "plan directory is outside a canonical lifecycle bucket", str(plan_root)))
    elif plan.get("lifecycle") != bucket:
        errors.append(Diagnostic("BUCKET_MISMATCH", f"manifest lifecycle {plan.get('lifecycle')!r} does not match {bucket!r}", "PLAN.yaml"))

    groups = manifest.get("groups")
    if not isinstance(groups, list) or len(groups) != len(EXPECTED_GROUPS):
        errors.append(Diagnostic("GROUP_COUNT", "exactly five ordered groups are required", "PLAN.yaml"))
        groups = []
    directories: list[str] = []
    for index, expected in enumerate(EXPECTED_GROUPS):
        actual = groups[index] if index < len(groups) and isinstance(groups[index], dict) else {}
        if (actual.get("id"), actual.get("order"), actual.get("directory")) != expected:
            errors.append(Diagnostic("GROUP_ORDER", f"group {index + 1} must be {expected}", "PLAN.yaml"))
        directory = actual.get("directory")
        if isinstance(directory, str):
            directories.append(directory)
    if len(set(directories)) != len(directories):
        errors.append(Diagnostic("GROUP_DUPLICATE", "group directories must be unique", "PLAN.yaml"))

    artifacts = _mapping(manifest.get("artifacts"))
    applicability = _mapping(manifest.get("applicability"))
    normalized: list[str] = []
    for key, value in artifacts.items():
        values = value if isinstance(value, list) else [value]
        for item in values:
            safe = contained_relative_path(item)
            if safe is None:
                errors.append(Diagnostic("ARTIFACT_PATH", f"unsafe artifact path for {key}: {item!r}", "PLAN.yaml"))
                continue
            normalized.append(safe)
            if safe != "README.md":
                owners = [directory for directory in directories if safe == directory or safe.startswith(directory + "/")]
                if len(owners) != 1:
                    errors.append(Diagnostic("ARTIFACT_OWNER", f"{safe} must have exactly one group owner", "PLAN.yaml"))
            applicability_key = ARTIFACT_APPLICABILITY.get(key, key)
            rule = str(applicability.get(applicability_key, "required"))
            if rule in {"required", "required_for_p0"} and not (plan_root / safe).exists():
                errors.append(Diagnostic("ARTIFACT_MISSING", f"declared artifact does not exist: {safe}", safe))
    if len(normalized) != len(set(normalized)):
        errors.append(Diagnostic("ARTIFACT_DUPLICATE", "normalized artifact paths must be unique", "PLAN.yaml"))
    if len(normalized) != len(flatten_paths(artifacts)):
        errors.append(Diagnostic("ARTIFACT_TYPE", "every artifact value must be a path or path list", "PLAN.yaml"))

    for key, rule in applicability.items():
        value = str(rule)
        allowed = {"required", "optional", "not_applicable", "required_for_p0"}
        if value not in allowed and not value.lower().startswith("n/a because "):
            errors.append(Diagnostic("APPLICABILITY", f"{key} has an unsupported applicability value", "PLAN.yaml"))
        if value in {"required", "required_for_p0"}:
            mapped = APPLICABILITY_ARTIFACTS.get(key)
            if mapped is None:
                errors.append(Diagnostic("APPLICABILITY_ARTIFACT", f"required applicability.{key} has no artifact mapping", "PLAN.yaml"))
            else:
                for artifact_key in mapped:
                    if artifact_key not in artifacts:
                        errors.append(Diagnostic("APPLICABILITY_ARTIFACT", f"applicability.{key} requires artifacts.{artifact_key}", "PLAN.yaml"))
    if tier in TIER_REQUIRED:
        for key in sorted(TIER_REQUIRED[tier]):
            if applicability.get(key) != "required":
                errors.append(Diagnostic("TIER_MATRIX", f"tier {tier} requires applicability.{key}=required", "PLAN.yaml"))
        if tier == "X" and applicability.get("discrimination_sensor") not in {"required", "required_for_p0"}:
            errors.append(Diagnostic("TIER_MATRIX", "tier X requires a P0-aware discrimination sensor", "PLAN.yaml"))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True, type=Path)
    args = parser.parse_args()
    return run_cli("validate_manifest", lambda: validate(args.plan.resolve()))


if __name__ == "__main__":
    raise SystemExit(main())
