# TASK-P3-03: Live Prospectus Extraction (Stage S2)

## Summary
- Executed Stage S2 Live Extraction across all 312 candidate prospectuses discovered in Stage S1.
- Retrieved and cached 309 primary prospectus documents in content-addressed cache (`cache/raw/<sha256>`).
- Successfully extracted 312 authoritative IPO records with strict separation between base shares and over-allotment/greenshoe shares.
- Captured 670 verbatim provenance evidence records with exact document character offsets and context snippets.
- Validated key 2026 landmark IPO extractions:
  - Anthropic (`ANT`): 980,000,000 shares @ $83.00 = $81,340,000,000.00 gross offering amount.
  - SpaceX (`SPCX`): 555,555,555 base shares @ $135.00 = $74,999,999,925.00 gross offering amount.
  - Aktis Oncology (`AKTS`): 17,650,000 shares @ $18.00 = $317,700,000.00 gross offering amount; 2,647,500 overallotment shares.
  - vVARDIS (`VVVV`): 9,722,223 shares @ $18.00 = $175,000,014.00 gross offering amount.
  - Windward Bio (`WWB`): 10,294,117 shares @ $17.00 = $174,999,989.00 gross offering amount.
  - Lycia Therapeutics (`LYCA`): 17,640,000 shares @ $18.00 = $317,520,000.00 gross offering amount.
  - BITGO (`BTGO`): 11,821,595 shares @ $18.00 = $212,788,710.00 gross offering amount.
  - York Space Systems (`YSS`): 18,500,000 shares @ $34.00 = $629,000,000.00 gross offering amount.
  - Applied Aerospace (`AADX`): 32,500,000 shares @ $20.00 = $650,000,000.00 gross offering amount.
- Saved outputs to `runs/RUN-2026-LIVE-001/extracted_records.json`, `runs/RUN-2026-LIVE-001/evidence.json`, and SQLite database (`ledger.sqlite`).

## Pre-Merge Gate Status
All pre-merge gates passed with 0 warnings:
- Ruff linting: PASSED
- Comment policy: PASSED
- Custom rules (IPO0xx): PASSED
- Mypy strict (40 source files): PASSED
- Pytest (24 unit tests): PASSED
