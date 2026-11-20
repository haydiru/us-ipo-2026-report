# Change Note - TASK-P2-07

## What Changed
- Implemented Stage S4: Computation and Arithmetic Audit in `src/ipo_ledger/pipeline/audit.py`.
- Recomputed all gross offering amounts dual-way (Decimal arithmetic and integer micro-units).
- Performed strict duplicate checks across CIKs and (ticker, pricing_date) tuples.
- Calculated headline totals for all IPOs and IPOs excluding SPACs.
- Emitted `audit_results.json` and saved results to SQLite.
- Added unit tests in `tests/unit/test_stage_s4.py`.

## What Could Break
- Any mathematical rounding discrepancy or duplicate record will immediately cause `audit_passed` to be `False`.
