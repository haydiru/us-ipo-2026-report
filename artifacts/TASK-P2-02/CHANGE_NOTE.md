# Change Note - TASK-P2-02

## What Changed
- Implemented `ContentCache` in `src/ipo_ledger/adapters/cache.py` storing raw payloads by SHA256 content address.
- Implemented `LedgerStorage` in `src/ipo_ledger/adapters/storage.py` providing relational SQLite storage for runs, candidates, exclusions, records, evidence, cross-checks, discrepancies, and audit/gate results.
- Added comprehensive unit tests in `tests/unit/test_adapters.py`.

## What Could Break
- Database path parent directories are created automatically, but foreign key constraints require valid run_id references.
