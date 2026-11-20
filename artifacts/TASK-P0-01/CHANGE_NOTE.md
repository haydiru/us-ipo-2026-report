# Change Note - TASK-P0-01

## What Changed
- Created repository layout per Section 8.1: `src/ipo_ledger/{domain, adapters, pipeline, report}`, `tests/`, `reference/`, `config/`, `.harness/`.
- Configured universe rules in `config/universe_rules.yaml`.
- Configured strict typing (`mypy`), linting (`ruff`), and imports in `pyproject.toml`.
- Created harness scripts: `check_comments.py`, `lint_custom.py`, `verify_workbook.py`, and `scripts/verify.py`.
- Created `.harness/EXPERIENCE.md`, `.harness/guardrails.md`, `.harness/tool_guidance.md`, and `.harness/feature_map.json`.

## What Could Break
- Stricter linter rules might reject unvalidated comments or domain imports if not adhered to.
- Banned APIs (e.g. `requests`, naive datetimes) will be rejected at the gate.
