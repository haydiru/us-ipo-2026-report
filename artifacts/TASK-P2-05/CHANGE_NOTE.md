# Change Note - TASK-P2-05

## What Changed
- Implemented Stage S2: Final Prospectus Extraction sub-tasks in `src/ipo_ledger/pipeline/extract.py`:
  - `extract_cover_page_terms()`: parses offer price, base shares, overallotment option, prospectus date, and security type.
  - Strict greenshoe separation: ensures over-allotment shares are never folded into base offering shares.
  - `validate_verbatim_presence()`: verifies exact string presence in cached source, recording character offset and surrounding snippet.
  - `create_ipo_record()`: builds immutable `IpoRecordModel` with validated Decimal computation.
- Added comprehensive unit tests in `tests/unit/test_stage_s2.py`.

## What Could Break
- Prospectuses with non-standard cover page formats or prices without verbatim presence will not produce evidence items, causing Stage S6 verification gates to catch them.
