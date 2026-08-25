#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import COMMIT_RE, print_errors
from loop_common import InvocationError, parse_front_matter

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--message", required=True)
    parser.add_argument("--task", type=Path)
    args = parser.parse_args()
    errors = []
    if args.task:
        try:
            metadata, _ = parse_front_matter(args.task)
            commit = metadata.get("commit") if isinstance(metadata.get("commit"), dict) else {}
            expected = commit.get("expected_message")
            if not isinstance(expected, str) or args.message.strip() != expected:
                errors.append(f"commit must exactly match task expected_message: {expected!r}")
        except InvocationError as exc:
            errors.append(str(exc))
    elif not COMMIT_RE.fullmatch(args.message.strip()):
        errors.append(
            "commit must match '<type>(<workflow>): task-NN - description' "
            "or '<type>(<workflow>): cr-NN - description'"
        )
    return print_errors(errors)

if __name__ == "__main__":
    raise SystemExit(main())
