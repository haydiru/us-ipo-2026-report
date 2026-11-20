# US IPO 2026 Report (Nasdaq & NYSE)

A pipeline and audited Excel workbook of U.S. IPOs priced on Nasdaq or NYSE from 2026-01-01 to 2026-11-20, built from SEC EDGAR Form 424B4 filings.

- **Deliverable:** [`output/us_ipo_report_2026.xlsx`](output/us_ipo_report_2026.xlsx) (Pass-2, After audit)
- **Audit summary:** [`AUDIT_REPORT.md`](AUDIT_REPORT.md)
- **Baseline (Pass-1, Before audit):** [`output/us_ipo_report_2026.pre_audit.xlsx`](output/us_ipo_report_2026.pre_audit.xlsx) and `runs/ledger.sqlite`, kept unmodified so the delta can be inspected
- **Spec:** [`prd.md`](prd.md) · **Code:** `src/ipo_ledger/` · **Tests:** `tests/`

Note: `cache/raw/` (about 1.1 GB of raw SEC filings) is not in this repo. The audit scripts need it to be re-downloaded from EDGAR.

## How this was built (AI conversation evidence)

### Step 1: PRD from my reusable PRD template

I first wrote the PRD with a PRD-generator conversation, using a PRD template that I keep upgrading from experience. The output had to be an `.xlsx`, so pages became pipeline stages and workbook sheets.

![PRD creation](docs/screenshots/01-prd-creation.png)

### Step 2: Execution of the PRD tasks in Antigravity

The agent was told: *"run all tasks in this prd.md, the result must be in xlsx and don't forget to audit the result."* It fetched SEC submissions and extracted filings into a cache.

![Antigravity 1](docs/screenshots/02-antigravity-1.png)
![Antigravity 2](docs/screenshots/03-antigravity-2.png)
![Antigravity 3](docs/screenshots/04-antigravity-3.png)
![Antigravity 4](docs/screenshots/05-antigravity-4.png)

### Step 3: Independent second-layer audit in Claude

A separate AI acted as an independent auditor on the Pass-1 workbook. It found about 100 of 283 rows wrong: placeholder values, a follow-on filing used instead of the IPO prospectus, greenshoe counted as base shares, filing dates used as pricing dates, NYSE American deals labelled NYSE, and non-IPO filings. It patched the workbook and wrote `AUDIT_REPORT.md`.

![Claude audit 1](docs/screenshots/06-claude-1.png)
![Claude audit 2](docs/screenshots/07-claude-2.png)
![Claude audit 3](docs/screenshots/08-claude-3.png)
![Claude audit 4](docs/screenshots/09-claude-4.png)

### Step 4: Final cleanups

The remaining unverified tickers were fetched live from SEC EDGAR and classified, and snapshot provenance was documented.

![Claude final cleanups](docs/screenshots/10-claude-5.png)

## Result after audit

241 verified IPOs (125 operating, 116 SPAC); $253.55B gross offering amount ($233.04B excluding SPACs). Known limitations are listed in `AUDIT_REPORT.md`.
