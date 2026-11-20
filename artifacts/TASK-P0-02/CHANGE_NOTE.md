# Change Note - TASK-P0-02

## What Changed
- Implemented branded types in `src/ipo_ledger/domain/types.py` (`Cik`, `AccessionNo`, `Ticker`, `UsdPerShare`, `ShareCount`, `UsdAmount`) with strict validating constructors.
- Implemented domain schemas, constants, and frozen Pydantic models in `src/ipo_ledger/domain/schema.py` (`CandidateModel`, `ExclusionModel`, `EvidenceModel`, `CrossCheckModel`, `DiscrepancyModel`, `AuditResultModel`, `IpoRecordModel`, `GateResultModel`, `RunManifestModel`).
- Implemented injectable `Clock` protocol and implementations (`SystemClock`, `FrozenClock`) in `src/ipo_ledger/clock.py`.
- Created golden reference implementations `reference/reference_stage.py` and `reference/reference_adapter.py`.

## What Could Break
- Passing non-validated strings to types will fail. Always use `parse_cik()`, `parse_ticker()`, etc.
- Passing floats to `parse_usd()` or `parse_share_count()` will raise `TypeError`.
