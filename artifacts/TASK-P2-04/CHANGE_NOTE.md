# Change Note - TASK-P2-04

## What Changed
- Implemented Stage S1: Universe Discovery in `src/ipo_ledger/pipeline/discover.py`.
- Parses EDGAR form index lines, classifies each candidate into qualifying IPO or Exclusion.
- Reconciles candidate tickers against exchange calendars and writes `unmatched_calendar.csv`.
- Created centralized `EdgarUrls` in `src/ipo_ledger/adapters/edgar.py` satisfying `IPO006`.
- Added unit tests in `tests/unit/test_stage_s1.py`.

## What Could Break
- Calendar entries without matching candidates in EDGAR will be flagged and written to `unmatched_calendar.csv`, which blocks Stage S6 Completeness Gate until reconciled.
