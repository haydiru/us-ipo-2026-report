# Tasks To Do

### Phase 0: Foundation & Harness
- [x] `TASK-P0-01`: Scaffold repository layout, configuration (`config/universe_rules.yaml`, `pyproject.toml`), and `.harness/` (`EXPERIENCE.md`, `guardrails.md`, `tool_guidance.md`, `feature_map.json`, custom linters `check_comments.py`, `lint_custom.py`, `verify_workbook.py`).
- [x] `TASK-P0-02`: Domain foundation: branded types (`domain/types.py`), schemas & constants (`domain/schema.py`), golden references (`reference/reference_stage.py`, `reference/reference_adapter.py`).
- [x] `TASK-P0-03`: Verification harness (`scripts/verify.py` or bash/powershell script) and negative gate test (verify broken code fails gates).

### Phase 1: Static Workbook Prototype
- [x] `TASK-P1-01`: Typed workbook builder (`report/workbook.py`) supporting all 6 sheets (`IPO_Report`, `Audit_Summary`, `Discrepancy_Log`, `Exclusions`, `Source_Evidence`, `Run_Metadata`) and generate prototype workbook with 5 representative rows.

### Phase 2: Pipeline Core & Fixture-based Testing
- [x] `TASK-P2-01`: Domain business logic: classification (`domain/classify.py`), computation & audit (`domain/compute.py`), reconciliation (`domain/reconcile.py`), completeness gate (`domain/gate.py`).
- [x] `TASK-P2-02`: Infrastructure adapters: content-addressed cache (`adapters/cache.py`), sqlite storage repository (`adapters/storage.py`), clock protocol (`clock.py`).
- [x] `TASK-P2-03`: Stage S0: Run Initialization (`pipeline/init_run.py`).
- [x] `TASK-P2-04`: Stage S1: Universe Discovery (`pipeline/discover.py`) with test fixtures.
- [x] `TASK-P2-05`: Stage S2: Extraction sub-tasks (cover-page parser, greenshoe separator, pricing-date resolver, URL & verbatim presence validator) (`pipeline/extract.py`).
- [x] `TASK-P2-06`: Stage S3: Cross-Verification (`pipeline/crosscheck.py`).
- [x] `TASK-P2-07`: Stage S4: Computation & Audit (`pipeline/audit.py`).
- [x] `TASK-P2-08`: Stage S5: Assembly & CLI orchestration (`pipeline/build.py`, `cli.py`).
- [x] `TASK-P2-09`: Stage S6: Completeness Gate (`pipeline/gate.py`) and full fixture flow verification (`verify:flow full`).

### Phase 3: Live EDGAR & Secondary-Source Integration & Audit
- [x] `TASK-P3-01`: EDGAR Client adapter (`adapters/edgar.py`) and secondary source adapters (`adapters/secondary/`).
- [x] `TASK-P3-02`: Execute Live Discovery (S1) for 2026-01-01 -> 2026-11-20, discover IPO candidates & log exclusions.
- [x] `TASK-P3-03`: Execute Live Extraction (S2) on 2026 prospectuses with verbatim evidence.
- [x] `TASK-P3-04`: Execute Live Cross-Verification (S3) against secondary sources.
- [x] `TASK-P3-05`: Execute Calculation & Audit (S4) and Workbook Assembly (S5) to emit `output/us_ipo_report_2026.xlsx`.
- [x] `TASK-P3-06`: Execute Completeness Gate (S6), run full workbook audit and produce final audit signoff.
