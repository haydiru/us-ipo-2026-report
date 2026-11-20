# Change Note - TASK-P1-01

## What Changed
- Implemented typed workbook builder in `src/ipo_ledger/report/workbook.py` creating all 6 sheets:
  - W1 `IPO_Report`: Frozen header, autofilter, real Excel dates, USD formatting, thousands separator, live Excel formulas (`=E{r}*F{r}`), real SEC hyperlinks, and flagged styling.
  - W2 `Audit_Summary`: Headline metrics (with and without SPACs), explicit confirmations, flagged breakdown, and limitations.
  - W3 `Discrepancy_Log`: All fields, sources, and conflict resolutions.
  - W4 `Exclusions`: Accession, company, reason code, and evidence links.
  - W5 `Source_Evidence`: Verbatim snippets, char offsets, and doc hashes.
  - W6 `Run_Metadata`: Reproducibility metadata and audit parameters.
- Generated sample static workbook prototype: `artifacts/TASK-P1-01/prototype_us_ipo_report_2026.xlsx`.
- Validated prototype using `.harness/scripts/verify_workbook.py`.

## What Could Break
- Adding unmapped columns to W1 without updating `domain/schema.py` and `COLUMN_WIDTHS_W1` will trigger validation failure.
