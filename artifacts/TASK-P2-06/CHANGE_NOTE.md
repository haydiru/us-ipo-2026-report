# Change Note - TASK-P2-06

## What Changed
- Implemented Stage S3: Cross-Verification against secondary sources in `src/ipo_ledger/pipeline/crosscheck.py`.
- Conducts field-level comparisons against secondary sources (Nasdaq, NYSE, financial providers).
- Generates `CrossCheckModel` for each source verified and records discrepancies in `DiscrepancyModel`.
- Applies precedence rules: primary final prospectus wins on offer price, base shares, and date; logs resolution rationale.
- Updates record status to `VERIFIED` or `FLAGGED` (`DISCREPANCY_RESOLVED`, `SINGLE_SOURCE`).
- Added unit tests in `tests/unit/test_stage_s3.py`.

## What Could Break
- Records with unverified field conflicts are flagged and will block the completeness gate if not cleanly resolved.
