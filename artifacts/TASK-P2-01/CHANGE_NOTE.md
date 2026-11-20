# Change Note - TASK-P2-01

## What Changed
- Implemented pure domain business logic:
  - `src/ipo_ledger/domain/classify.py`: Classifies filings into qualifying IPO, SPAC unit, or specific exclusion codes (`FOLLOW_ON`, `DIRECT_LISTING`, `DE_SPAC`, `FUND`, `WRONG_VENUE`, `UNPRICED`).
  - `src/ipo_ledger/domain/compute.py`: Decimal calculation of gross offering amount with independent micro-unit integer recompute, record math audit, dual-sum aggregate totals, and duplicate detection.
  - `src/ipo_ledger/domain/reconcile.py`: Cross-check field-by-field comparison, conflict resolution with primary prospectus precedence, and greenshoe over-allotment detection.
  - `src/ipo_ledger/domain/gate.py`: Mechanical evaluation of 6 mandatory completeness conditions to decide `VERIFIED` vs `DRAFT_INCOMPLETE`.
- Implemented comprehensive unit tests in `tests/unit/test_domain_logic.py`.

## What Could Break
- Any violation of purity in `domain/` (e.g. importing network, db, or naive clock) will fail linter and architectural boundary checks.
