#!/usr/bin/env python3
"""Shared WetoLoop contracts called by the individual validator entrypoints."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from loop_common import Diagnostic, InvocationError, contained_relative_path, load_manifest, parse_front_matter, read_utf8

REQUIREMENT_RE = re.compile(r"\b[A-Z][A-Z0-9]*(?:-[A-Z][A-Z0-9]*)*-\d{3}\b")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


def mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def artifact(plan_root: Path, manifest: dict[str, Any], key: str) -> Path:
    value = mapping(manifest.get("artifacts")).get(key)
    if not isinstance(value, str):
        raise InvocationError(f"artifact {key} is not declared")
    return plan_root / value


def validate_document(plan_root: Path, key: str) -> list[Diagnostic]:
    manifest = load_manifest(plan_root)
    path = artifact(plan_root, manifest, key)
    text = read_utf8(path)
    errors: list[Diagnostic] = []
    if not text.lstrip().startswith("#") or len(text.strip()) < 100:
        errors.append(Diagnostic("DOCUMENT_CONTRACT", f"{key} must contain a meaningful Markdown contract", str(path)))
    if "{{" in text or "}}" in text:
        errors.append(Diagnostic("DOCUMENT_PLACEHOLDER", f"{key} contains unresolved template placeholders", str(path)))
    return errors


def task_graph(plan_root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Path], list[Diagnostic]]:
    manifest = load_manifest(plan_root)
    task_dir = artifact(plan_root, manifest, "tasks_directory")
    errors: list[Diagnostic] = []
    tasks: dict[str, dict[str, Any]] = {}
    paths: dict[str, Path] = {}
    if not task_dir.is_dir():
        return tasks, paths, [Diagnostic("TASK_DIR", "task directory is missing", str(task_dir))]
    for path in sorted(task_dir.glob("*.md")):
        try:
            metadata, _ = parse_front_matter(path)
        except InvocationError as exc:
            errors.append(Diagnostic("TASK_PARSE", str(exc), str(path)))
            continue
        task_id = metadata.get("id")
        if not isinstance(task_id, str) or not re.fullmatch(r"T\d{2,}", task_id):
            errors.append(Diagnostic("TASK_ID", "canonical task ID is required", str(path)))
            continue
        if task_id in tasks:
            errors.append(Diagnostic("TASK_DUPLICATE", f"duplicate task ID {task_id}", str(path)))
        tasks[task_id] = metadata
        paths[task_id] = path

    for task_id, task in sorted(tasks.items()):
        dependencies = task.get("depends_on")
        if not isinstance(dependencies, list):
            errors.append(Diagnostic("TASK_DEPENDENCIES", f"{task_id} depends_on must be a list", str(paths[task_id])))
            continue
        for dependency in dependencies:
            if dependency not in tasks:
                errors.append(Diagnostic("TASK_DEPENDENCY_MISSING", f"{task_id} depends on unknown {dependency}", str(paths[task_id])))
        status = task.get("status")
        commit = mapping(task.get("commit"))
        if status == "completed":
            sha = commit.get("sha")
            if not isinstance(sha, str) or not COMMIT_RE.fullmatch(sha):
                errors.append(Diagnostic("TASK_COMMIT", f"{task_id} completed without a 40-character SHA", str(paths[task_id])))
            if not isinstance(task.get("evidence"), list) or not task["evidence"]:
                errors.append(Diagnostic("TASK_EVIDENCE", f"{task_id} completed without evidence", str(paths[task_id])))
            if task.get("reviewer") in {None, "", "unassigned", task.get("builder")}:
                errors.append(Diagnostic("TASK_REVIEW", f"{task_id} completed without independent reviewer", str(paths[task_id])))
        if status == "blocked" and not isinstance(task.get("blocker"), dict):
            errors.append(Diagnostic("TASK_BLOCKER", f"{task_id} blocked without structured blocker", str(paths[task_id])))
        if status in {"cancelled", "superseded"} and not task.get("terminal_reason"):
            errors.append(Diagnostic("TASK_TERMINAL", f"{task_id} terminal without reason", str(paths[task_id])))

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            errors.append(Diagnostic("TASK_CYCLE", f"dependency cycle includes {task_id}", str(paths[task_id])))
            return
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in tasks[task_id].get("depends_on", []):
            if dependency in tasks:
                visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in sorted(tasks):
        visit(task_id)
    return tasks, paths, errors


def validate_tasks_contract(plan_root: Path) -> list[Diagnostic]:
    return task_graph(plan_root)[2]


def validate_traceability_contract(plan_root: Path) -> list[Diagnostic]:
    manifest = load_manifest(plan_root)
    tasks, _, errors = task_graph(plan_root)
    requirements_text = read_utf8(artifact(plan_root, manifest, "requirements"))
    approved = set(REQUIREMENT_RE.findall(requirements_text))
    owners: dict[str, list[str]] = {}
    for task_id, task in tasks.items():
        requirements = task.get("requirements") if isinstance(task.get("requirements"), list) else []
        for requirement in requirements:
            owners.setdefault(str(requirement), []).append(task_id)
            if requirement not in approved:
                errors.append(Diagnostic("TRACE_UNKNOWN", f"{task_id} owns unknown requirement {requirement}"))
    for requirement in sorted(approved):
        assigned = owners.get(requirement, [])
        if len(assigned) != 1:
            errors.append(Diagnostic("TRACE_OWNER", f"{requirement} must have exactly one task owner; found {assigned}"))
    tasks_index = read_utf8(artifact(plan_root, manifest, "tasks_index"))
    for task_id in sorted(tasks):
        if task_id not in tasks_index:
            errors.append(Diagnostic("TASK_BACKLINK", f"{task_id} is absent from TASKS.md"))
    return errors


def validate_execution_state_contract(plan_root: Path) -> list[Diagnostic]:
    manifest = load_manifest(plan_root)
    applicability = mapping(manifest.get("applicability"))
    tasks_applicable = applicability.get("tasks") in {"required", "required_for_p0"}
    if tasks_applicable:
        tasks, _, errors = task_graph(plan_root)
    else:
        tasks, errors = {}, []
    state_path = artifact(plan_root, manifest, "state")
    state, _ = parse_front_matter(state_path)
    current = mapping(state.get("current"))
    current_task = tasks.get(str(current.get("task")))
    if tasks_applicable and (current_task is None or current_task.get("status") != current.get("status")):
        errors.append(Diagnostic("STATE_CURRENT", "STATE current task/status must match task front matter", str(state_path)))
    if not tasks_applicable and current.get("task") not in {None, "null"}:
        errors.append(Diagnostic("STATE_CURRENT", "STATE current task must be null when tasks are not applicable", str(state_path)))
    completed = sorted(task_id for task_id, task in tasks.items() if task.get("status") == "completed")
    if sorted(state.get("completed_tasks", [])) != completed:
        errors.append(Diagnostic("STATE_COMPLETED", "STATE completed_tasks must equal completed task files", str(state_path)))

    producers = state.get("producers") if isinstance(state.get("producers"), list) else []
    run_ids = [item.get("run_id") for item in producers if isinstance(item, dict)]
    producer_tasks = [item.get("task") for item in producers if isinstance(item, dict)]
    if len(run_ids) != len(set(run_ids)) or any(not isinstance(item, str) or not item for item in run_ids):
        errors.append(Diagnostic("PRODUCER_UNIQUE", "producer Run IDs must be non-empty and unique", str(state_path)))
    if len(producer_tasks) != len(set(producer_tasks)):
        errors.append(Diagnostic("PRODUCER_TASK_UNIQUE", "each task must have at most one evidence producer", str(state_path)))

    for task_id in completed:
        task = tasks[task_id]
        sha = mapping(task.get("commit")).get("sha")
        evidence_paths = task.get("evidence") if isinstance(task.get("evidence"), list) else []
        matching = [item for item in producers if isinstance(item, dict) and item.get("task") == task_id]
        zero_reasons: list[str] = []
        if len(matching) != 1:
            zero_reasons.append("exactly one producer is required")
        producer = matching[0] if len(matching) == 1 else {}
        run_id = producer.get("run_id")
        artifact_reference = producer.get("evidence")
        if producer.get("result") != "pass":
            zero_reasons.append("producer result must be pass")
        if not isinstance(run_id, str) or not run_id:
            zero_reasons.append("producer Run ID is required")
        safe_task_evidence = [contained_relative_path(item) for item in evidence_paths]
        safe_artifact_reference = contained_relative_path(artifact_reference)
        if any(item is None for item in safe_task_evidence):
            zero_reasons.append("task evidence paths must be contained relative paths")
        if safe_artifact_reference is None:
            zero_reasons.append("producer artifact reference must be a contained relative path")
        if not isinstance(artifact_reference, str) or artifact_reference not in evidence_paths:
            zero_reasons.append("producer artifact reference must equal task evidence")
        if len(evidence_paths) != 1:
            zero_reasons.append("one canonical evidence artifact is required")
        if safe_artifact_reference is not None:
            evidence_path = (plan_root / safe_artifact_reference).resolve()
            if plan_root.resolve() not in {evidence_path, *evidence_path.parents}:
                zero_reasons.append("artifact reference escapes the plan root")
                evidence_path = plan_root / "__escaped_evidence__"
            if not evidence_path.is_file():
                zero_reasons.append("artifact reference does not exist")
            else:
                evidence_text = read_utf8(evidence_path)
                commit_values = re.findall(r"(?m)^- Candidate commit:\s*`([0-9a-f]{40})`\s*$", evidence_text)
                run_values = re.findall(r"(?m)^- Run ID:\s*`([^`]+)`\s*$", evidence_text)
                result_values = re.findall(r"(?mi)^Final result:\s*`?(PASS|FAIL|BLOCK|ERROR)`?\s*$", evidence_text)
                if not result_values:
                    result_values = re.findall(
                        r"(?mi)^Independent staged-diff re-review:\s*`?(PASS|FAIL|BLOCK|ERROR)`?(?:\s*,.*)?$",
                        evidence_text,
                    )
                if not isinstance(sha, str) or commit_values != [sha]:
                    zero_reasons.append("commit freshness anchor is absent")
                if not isinstance(run_id, str) or run_values != [run_id]:
                    zero_reasons.append("producer Run ID is absent from artifact")
                if result_values != ["PASS"]:
                    zero_reasons.append(f"canonical final result must be exactly PASS; found {result_values}")
        if zero_reasons:
            errors.append(Diagnostic("EVIDENCE_ZERO", f"{task_id} evidence evaluates to zero: {', '.join(zero_reasons)}", str(state_path)))
    return errors
