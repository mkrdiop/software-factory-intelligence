#!/usr/bin/env python3
"""Validate SFI-03 JSON fixtures against the Draft 2020-12 schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas/v1/sfi-03.schema.json"
FIXTURE_ROOT = ROOT / "fixtures/v1"


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    expected = {"valid": True, "invalid": False}
    failures: list[str] = []
    counts: dict[str, int] = {}

    for category, should_validate in expected.items():
        paths = sorted((FIXTURE_ROOT / category).glob("*.json"))
        if not paths:
            failures.append(f"{category}: no fixtures found")
            continue
        counts[category] = len(paths)

        for path in paths:
            try:
                instance = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                failures.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
                continue

            errors = sorted(
                validator.iter_errors(instance),
                key=lambda error: (list(map(str, error.absolute_path)), error.message),
            )
            passed = not errors
            if passed != should_validate:
                details = "; ".join(
                    f"/{'/'.join(map(str, error.absolute_path))}: {error.message}"
                    for error in errors[:5]
                )
                failures.append(
                    f"{path.relative_to(ROOT)}: expected "
                    f"{'valid' if should_validate else 'invalid'}, got "
                    f"{'valid' if passed else 'invalid'}"
                    + (f" ({details})" if details else "")
                )
            else:
                print(f"PASS {path.relative_to(ROOT)}")

    print(
        "SFI-03 fixture summary: "
        + ", ".join(f"{key}={value}" for key, value in counts.items())
    )
    if failures:
        print("\n".join(f"FAIL {failure}" for failure in failures), file=sys.stderr)
        return 1
    print("SFI-03 Draft 2020-12 schema and fixture checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
