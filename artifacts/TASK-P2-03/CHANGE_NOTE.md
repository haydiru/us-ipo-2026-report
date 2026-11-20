# Change Note - TASK-P2-03

## What Changed
- Implemented Stage S0: Run Initialization and Configuration in `src/ipo_ledger/pipeline/init_run.py`.
- Validates `config/universe_rules.yaml` schema, window dates (`window_start <= window_end == as_of_date`), and hashes configuration.
- Freezes immutable `RunManifestModel` and persists to `runs/<run_id>/manifest.json` and SQLite database `ledger.sqlite`.
- Added unit tests in `tests/unit/test_stage_s0.py`.

## What Could Break
- Mismatched `window_end` and `as_of_date` or missing config file will immediately halt run initialization with a descriptive validation error.
