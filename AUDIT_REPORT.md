# AUDIT_REPORT — US IPO 2026 Workbook (Second-Layer Independent Audit)

**Verdict: the original workbook failed audit; it was patched and now passes.** The original "100% pass" gate only re-multiplied `E×F`. It never checked inputs against the filings. About 100 of 283 rows were wrong (placeholder values, wrong filing, wrong venue, non-IPOs).

## 1. Executive Verdict & Accuracy Scorecard

| Stage | Count |
|---|---|
| SEC 424B4 filings indexed (`cache/all_2026_424b4.json`) | 475 (472 in `ledger.sqlite`: 312 candidates + 160 exclusions) |
| Excluded (231 total) | Follow-ons 151 · De-SPAC 3 · Non-Nasdaq/NYSE 24 · Duplicates 29 · Direct listings/resales 20 · Notes/funds 4 |
| **Final verified IPOs** | **241** (125 operating + 116 SPAC), down from 283 |
| Gross offering amount | **$253.55B** all · **$233.04B** ex-SPAC (was $240.1B / $218.4B) |
| Formula integrity | **241/241 (100%)** live `=E*F`, 0 errors, valid EDGAR links |
| Cover-page match (price and base shares) | 241/241 (240 scripted, 1 by hand) |

- **Benchmark:** 125 operating IPOs is inside the 106–140 range. The 241 total is below the ~255–295 benchmark, so the universe may be incomplete (see §4).
- **Also clean:** no duplicates, weekend/holiday dates or `#REF!`. Only Nasdaq and NYSE remain.

## 2. How Grounding Was Achieved

1. **Discovery:** the EDGAR full index lists 424B4 filings (deterministic code).
2. **Extraction:** covers are cached by SHA-256 with verbatim evidence snippets.
3. **Cross-check:** a script compares Nasdaq/NYSE/press sources and logs discrepancies.
4. **Audit (this layer):** an independent parser re-derived price and base shares from the cover table (total ÷ price), kept the greenshoe separate, picked the earliest "initial public offering" 424B4 per CIK, and read exchange and prospectus date.

## 3. Before vs. After (full list: `Discrepancy_Log`, resolver = `independent_audit`)

| Ticker | Field | Before | After (SEC 424B4) | Root cause / method |
|---|---|---|---|---|
| FPS | Price × shares | $49.00 × 43,650,000 (acc …294982, Jul-02) | **$27.00 × 56,000,000** (0001193125-26-040029, Feb-04) | Later follow-on used. Cover total $1,512,000,000 ÷ $27 |
| MANE | Price × shares | $100 × 3,843,790 | **$17 × 15,077,647** (0001628280-26-005505) | Wrong filing. Cover table |
| BRKH | Base shares | 1,200,000 | **8,000,000** | Greenshoe option captured as base |
| FVAV | Base shares | 10,000,000 | **25,000,000** | Placeholder default. Greenshoe 3.75M excluded |
| TRAD | Offer price | $20.00 | **$10.00** | `$20.00` and `10,000,000` defaults found in ~40 rows |
| CBRS | Pricing date | 2026-05-14 | **2026-05-13** | EDGAR filing date used (T+1). Cover "date of this prospectus" |
| TP | Exchange | NYSE | **Removed** | Cover: "approved for listing on NYSE American" (11 such deals) |
| MDLN | $35.50 × 60M | Included | **Removed** | Already Nasdaq-listed secondary (cover cites closing price) |

- **Pipeline's own log contradicted its output:** in 47 of 55 `Discrepancy_Log` entries the logged resolution was *not* what the workbook shipped (e.g. FPS logged $27 and shipped $49).
- **Pricing dates:** 119 rows were corrected from filing date to prospectus or underwriting-agreement date.
- **Non-IPOs removed:** 18 direct-listing/resale registrations (placeholder $20.00), 7 already-listed follow-ons, notes and fund documents.
- **Accessions repointed:** 12 rows now cite the IPO prospectus.

## 4. Unresolved Data & Known Limitations

- **Pricing-date proxy:** **83 rows** are `FLAGGED` `PRICING_DATE_FILING_PROXY` because no prospectus or underwriting date was parseable. True pricing is typically 1–2 business days earlier.
- **Single source:** every row rests on the 424B4 cover alone (cache only; the sole live EDGAR query was BRAI/WSHP).
- **Total below benchmark:** 241 vs ~255–295. Causes: 24 non-Nasdaq/NYSE exclusions, plus possible 424B1/424B4 filings absent from the index, or deals after the 2026-11-20 snapshot. Not resolved.
- **BRAI, WSHP:** fetched live from SEC EDGAR (cached in `cache/live_audit/`). Both are resale registrations with no offer price, not 2026 IPOs; kept in `Exclusions` (`DIRECT_LISTING_RESALE`). Counts unchanged.
- **ADS of foreign-listed issuers** (e.g. SK hynix, $26.5B) are kept as US ADS IPOs. A reviewer may exclude them.
- **Snapshot provenance:** `output/us_ipo_report_2026.pre_audit.xlsx` and `runs/ledger.sqlite` are intentionally preserved, unmodified, as the **Pass-1 (Before)** baseline (283 records). `output/us_ipo_report_2026.xlsx` is the **Pass-2 (After)** deliverable.
## 5. 3-Minute Reviewer Guide (`output/us_ipo_report_2026.xlsx`)

1. **`Audit_Summary`:** totals 241 / 125, $253.55B, pass rate 100%, limitations. Column C holds live formulas that match.
2. **`IPO_Report` row 242: ANT** (largest). $83.00 × 980,000,000 = $81.34B. Accession **0001628280-26-074944**. Open the link and confirm the cover table.
3. **`IPO_Report` row 32: FPS** (corrected row). $27.00 × 56,000,000. Accession **0001193125-26-040029**. Compare with `Discrepancy_Log` rows 187–190, which show the old $49.00 × 43.65M.
4. **`IPO_Report` row 59: FVAV** (SPAC row). $10.00 × 25,000,000. Accession **0001213900-26-020875**. `Discrepancy_Log` row 86 shows 10M → 25M. `Source_Evidence` holds the verbatim snippet and SHA-256.
5. **`Exclusions`:** filter on `WRONG_VENUE_NYSE_AMERICAN` or `DIRECT_LISTING_RESALE`.

Reproduce: `python scripts/audit_verify_final.py`
