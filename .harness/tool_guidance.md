# Tool Guidance & Commands

## Environment & Commands
- **Python:** Python 3.13 / 3.12+
- **Run verify suite:** `python scripts/verify.py`
- **Linting:** `python -m ruff check src tests`
- **Type checking:** `python -m mypy --strict src tests`
- **Import linter:** `python -m importlinter.cli`
- **Comment policy checker:** `python .harness/scripts/check_comments.py`
- **Custom rule checker:** `python .harness/scripts/lint_custom.py`
- **Workbook verification:** `python .harness/scripts/verify_workbook.py <path_to_xlsx>`
- **Run pipeline:** `python -m ipo_ledger.cli <stage>`
