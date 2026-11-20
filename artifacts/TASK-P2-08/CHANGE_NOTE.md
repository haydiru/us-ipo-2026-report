# Change Note - TASK-P2-08

## What Changed
- Implemented Stage S5: Assembly Orchestrator in `src/ipo_ledger/pipeline/build.py` connecting pipeline data to `build_workbook()`.
- Implemented CLI entry point in `src/ipo_ledger/cli.py` supporting `init`, `discover`, `extract`, `crosscheck`, `audit`, `build`, and `gate` subcommands.
- Added unit tests in `tests/unit/test_stage_s5.py`.

## What Could Break
- Command execution without required arguments (e.g. invalid config path) exits with non-zero code.
