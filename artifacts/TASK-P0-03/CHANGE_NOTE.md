# Change Note - TASK-P0-03

## What Changed
- Implemented `tests/unit/test_negative_gates.py` testing negative constraints and footguns:
  - Rejection of float values in `UsdPerShare` (TypeError)
  - Rejection of float values in `UsdAmount` (TypeError)
  - Rejection of float values in `ShareCount` (TypeError)
  - Rejection of zero or negative prices and shares (ValueError)
  - Validation of positive test cases (CIK padding, uppercase ticker, clean USD parsing)
- Added pytest execution to `scripts/verify.py` with proper PYTHONPATH resolution.
- Configured pytest options and filter warnings in `pyproject.toml`.

## What Could Break
- Any pipeline change that attempts to pass float money will fail this test suite.
