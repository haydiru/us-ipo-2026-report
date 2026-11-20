# TASK-P3-05: Calculation & Audit (Stage S4) and Workbook Assembly (Stage S5)

## Summary
- Executed Stage S4 Calculation & Arithmetic Audit:
  - Deduplicated candidate pool by CIK to guarantee one IPO per issuer per PRD Section 3.5, retaining the definitive priced prospectus for 283 unique companies and logging 29 superseded/duplicate filings in `Exclusions` with code `DUPLICATE`.
  - Zero duplicate keys across both `(CIK)` and `(ticker, pricing_date)`.
  - Dual-method arithmetic verification: compared Decimal calculations quantized to cents (`ROUND_HALF_EVEN`) against integer micro-dollar recomputation (`shares × price_in_1e4_units`).
  - Arithmetic audit passed with 0 delta across all rows and aggregate sums.
  - Total Gross Capital Raised (All 283 IPOs): $240,107,864,980.94
  - Total Gross Capital Raised (Excluding SPACs): $218,351,774,685.74
- Executed Stage S5 Typed Workbook Assembly:
  - Assembled `Task1/output/us_ipo_report_2026.xlsx` containing all 6 required sheets:
    - Sheet 1: `IPO_Report` (283 rows sorted chronologically by Pricing Date, live Excel formula `=E{r}*F{r}`, Consolas formatting, clickable 424B4 hyperlinks).
    - Sheet 2: `Audit_Summary` (structured metrics breakdown by exchange, operating vs SPAC deals, totals).
    - Sheet 3: `Discrepancy_Log` (55 resolved cross-verification discrepancies with rationales).
    - Sheet 4: `Exclusions` (189 logged exclusions with explicit audit reason codes).
    - Sheet 5: `Source_Evidence` (670 verbatim provenance records with char offsets).
    - Sheet 6: `Run_Metadata` (manifest, hashes, coverage window).
  - Mirrored output workbook to `c:\Website\AI\output\us_ipo_report_2026.xlsx`.
  - Verified workbook structure with `.harness/scripts/verify_workbook.py`: SUCCESS.

## Pre-Merge Gate Status
All pre-merge gates passed with 0 warnings:
- Ruff linting: PASSED
- Comment policy: PASSED
- Custom rules (IPO0xx): PASSED
- Mypy strict (40 source files): PASSED
- Pytest (24 unit tests): PASSED
