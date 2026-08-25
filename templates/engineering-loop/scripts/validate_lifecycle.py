#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from loop_common import Diagnostic, lifecycle_bucket, load_manifest, parse_front_matter, read_utf8, run_cli
from loop_checks import validate_execution_state_contract

TRANSITIONS = {
    "backlog": {"in_progress"},
    "in_progress": {"done", "backlog"},
    "done": set(),
}

READINESS_RE = re.compile(r"(?m)^\s*`?READY_FOR_EXECUTION:\s*(YES|NO)`?\s*$")
APPROVAL_RE = re.compile(
    r"(?m)^\s*(?:Status:\s*)?`?"
    r"(APPROVED_FOR_EXECUTION|PENDING_OWNER_APPROVAL|PENDING_MIGRATION_APPROVAL|APPROVED|REJECTED)"
    r"`?\s*$"
)


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _artifact(plan_root: Path, manifest: dict[str, Any], name: str) -> Path:
    artifacts = _mapping(manifest.get("artifacts"))
    value = artifacts.get(name)
    return plan_root / value if isinstance(value, str) else plan_root / "__missing__"


def _duplicate_ids(plan_root: Path, plan_id: str) -> tuple[list[Path], list[Diagnostic]]:
    plans_root = plan_root.parent.parent
    matches: list[Path] = []
    errors: list[Diagnostic] = []
    for bucket in ("_backlog", "_in_progress", "_done", "_cancelled", "_superseded"):
        root = plans_root / bucket
        if not root.is_dir():
            continue
        for manifest_path in root.glob("*/PLAN.yaml"):
            candidate = manifest_path.parent.resolve()
            if candidate == plan_root.resolve():
                continue
            try:
                candidate_manifest = load_manifest(candidate)
            except Exception as exc:
                errors.append(Diagnostic("COLLISION_SCAN", f"cannot validate candidate manifest: {exc}", str(manifest_path)))
                continue
            if _mapping(candidate_manifest.get("plan")).get("id") == plan_id:
                matches.append(candidate)
    return sorted(matches), errors


def _backlink_errors(plan_root: Path) -> list[Diagnostic]:
    errors: list[Diagnostic] = []
    link_re = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    for document in sorted(plan_root.rglob("*.md")):
        text = read_utf8(document)
        for match in link_re.finditer(text):
            raw = match.group(1).strip().strip("<>")
            target = raw.split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:", "/")) or "{{" in target:
                continue
            resolved = (document.parent / target).resolve()
            if plan_root.resolve() not in {resolved, *resolved.parents}:
                errors.append(Diagnostic("BACKLINK_ESCAPE", f"relative link escapes the activity: {raw}", str(document)))
            elif not resolved.exists():
                errors.append(Diagnostic("BACKLINK_BROKEN", f"relative link target does not exist: {raw}", str(document)))
    return errors


def _external_backlinks(plan_root: Path) -> list[Diagnostic]:
    plans_root = plan_root.parent.parent
    relative = plan_root.relative_to(plans_root).as_posix()
    errors: list[Diagnostic] = []
    for document in sorted(plans_root.rglob("*.md")):
        if plan_root.resolve() in {document.resolve(), *document.resolve().parents}:
            continue
        text = read_utf8(document).replace("\\", "/")
        if relative in text:
            errors.append(Diagnostic("BACKLINK_EXTERNAL", f"external backlink requires move reconciliation: {relative}", str(document)))
    return errors


def _gate_f(plan_root: Path, manifest: dict[str, Any]) -> list[Diagnostic]:
    errors: list[Diagnostic] = []
    readiness = _artifact(plan_root, manifest, "readiness")
    approval = _artifact(plan_root, manifest, "approval_record")
    readiness_text = read_utf8(readiness) if readiness.is_file() else ""
    approval_text = read_utf8(approval) if approval.is_file() else ""
    readiness_values = READINESS_RE.findall(readiness_text)
    if readiness_values != ["YES"]:
        errors.append(Diagnostic(
            "GATE_F_READY",
            f"exactly one authoritative READY_FOR_EXECUTION: YES is required; found {readiness_values}",
            str(readiness),
        ))
    approval_values = APPROVAL_RE.findall(approval_text)
    if approval_values != ["APPROVED_FOR_EXECUTION"]:
        errors.append(Diagnostic(
            "GATE_F_APPROVAL",
            f"exactly one authoritative APPROVED_FOR_EXECUTION status is required; found {approval_values}",
            str(approval),
        ))
    repository = _mapping(manifest.get("repository"))
    if repository.get("single_writer") is not True:
        errors.append(Diagnostic("GATE_F_WRITER", "repository.single_writer must be true", "PLAN.yaml"))
    if not repository.get("working_branch") or not repository.get("approved_base_sha"):
        errors.append(Diagnostic("GATE_F_GIT", "working branch and approved base SHA are required", "PLAN.yaml"))
    return errors


def _gate_g(plan_root: Path, manifest: dict[str, Any]) -> list[Diagnostic]:
    errors: list[Diagnostic] = []
    errors.extend(validate_execution_state_contract(plan_root))
    task_dir = _artifact(plan_root, manifest, "tasks_directory")
    for task_path in sorted(task_dir.glob("*.md")) if task_dir.is_dir() else []:
        try:
            metadata, _ = parse_front_matter(task_path)
        except Exception as exc:
            errors.append(Diagnostic("GATE_G_TASK_PARSE", str(exc), str(task_path)))
            continue
        commit = _mapping(metadata.get("commit"))
        if metadata.get("status") != "completed" or not isinstance(commit.get("sha"), str) or len(commit["sha"]) != 40:
            errors.append(Diagnostic("GATE_G_TASK", f"{metadata.get('id', task_path.name)} lacks completed status and commit", str(task_path)))
        if not metadata.get("reviewer") or metadata.get("reviewer") in {"unassigned", metadata.get("builder")}:
            errors.append(Diagnostic("GATE_G_REVIEW", "independent task reviewer is required", str(task_path)))
        if not metadata.get("evidence"):
            errors.append(Diagnostic("GATE_G_EVIDENCE", "task evidence is required", str(task_path)))

    report = _artifact(plan_root, manifest, "validation_report")
    report_text = read_utf8(report).upper() if report.is_file() else ""
    required_report = {
        "PACKAGE GATE": "PASS",
        "INDEPENDENT FINAL REVIEW": "PASS",
        "READY_FOR_PR": "YES",
    }
    for label, value in required_report.items():
        if f"{label}: {value}" not in report_text:
            errors.append(Diagnostic("GATE_G_REPORT", f"{label}: {value} is required", str(report)))
    if "ECOSYSTEM REGRESSION: PASS" not in report_text and "ECOSYSTEM REGRESSION: PENDING" not in report_text:
        errors.append(Diagnostic("GATE_G_ECOSYSTEM", "ecosystem regression must be PASS or explicitly PENDING", str(report)))
    return errors


def validate(plan_root: Path, transition_to: str | None = None, destination: Path | None = None) -> list[Diagnostic]:
    manifest = load_manifest(plan_root)
    plan = _mapping(manifest.get("plan"))
    current = lifecycle_bucket(plan_root)
    errors: list[Diagnostic] = []
    plan_id = plan.get("id")
    if not isinstance(plan_id, str) or not plan_id:
        errors.append(Diagnostic("PLAN_ID", "plan.id is required", "PLAN.yaml"))
    else:
        duplicates, scan_errors = _duplicate_ids(plan_root, plan_id)
        errors.extend(scan_errors)
        for duplicate in duplicates:
            errors.append(Diagnostic("PLAN_COLLISION", f"duplicate plan ID at {duplicate}", "PLAN.yaml"))
    manifest_lifecycle = plan.get("lifecycle")
    if current is None or manifest_lifecycle != current:
        errors.append(Diagnostic("BUCKET_MISMATCH", f"physical bucket {current!r} and manifest lifecycle {manifest_lifecycle!r} must agree", "PLAN.yaml"))
    errors.extend(_backlink_errors(plan_root))
    if transition_to is None:
        if current == "in_progress":
            errors.extend(_gate_f(plan_root, manifest))
        if current == "done":
            errors.extend(_gate_g(plan_root, manifest))
    else:
        if current is None or transition_to not in TRANSITIONS.get(current, set()):
            errors.append(Diagnostic("TRANSITION", f"transition {current!r} -> {transition_to!r} is not allowed"))
        elif transition_to == "in_progress":
            errors.extend(_gate_f(plan_root, manifest))
        elif transition_to == "done":
            errors.extend(_gate_g(plan_root, manifest))
        if destination is None:
            errors.append(Diagnostic("DESTINATION_REQUIRED", "transition validation requires an exact destination"))
        else:
            resolved_destination = destination.resolve()
            expected_parent = plan_root.parent.parent / {
                "backlog": "_backlog",
                "in_progress": "_in_progress",
                "done": "_done",
                "cancelled": "_cancelled",
                "superseded": "_superseded",
            }[transition_to]
            if resolved_destination.parent != expected_parent.resolve():
                errors.append(Diagnostic("DESTINATION_BUCKET", f"destination must be an immediate child of {expected_parent}"))
            if resolved_destination.exists():
                errors.append(Diagnostic("DESTINATION_COLLISION", f"destination already exists: {resolved_destination}"))
            errors.extend(_external_backlinks(plan_root))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--transition-to", choices=sorted(TRANSITIONS))
    parser.add_argument("--destination", type=Path)
    args = parser.parse_args()
    return run_cli("validate_lifecycle", lambda: validate(args.plan.resolve(), args.transition_to, args.destination))


if __name__ == "__main__":
    raise SystemExit(main())
