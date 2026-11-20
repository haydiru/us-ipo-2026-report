"""Analyze discovery and classification of all 424B4 filings in 2026."""

import json
import os

with open("cache/all_2026_424b4.json", encoding="utf-8") as f:
    filings = json.load(f)

print(f"Total filings: {len(filings)}")

candidates = []
exclusions = []

for item in filings:
    cik = item["cik"]
    sub_path = f"cache/submissions/{cik}.json"
    if not os.path.exists(sub_path):
        continue
    with open(sub_path, encoding="utf-8") as f:
        sub = json.load(f)

    comp_name = sub.get("name", item["company_name"])
    tickers = sub.get("tickers", [])
    ticker = (tickers[0] if tickers else "") or ""
    exchanges = sub.get("exchanges", [])
    exchange = (exchanges[0] if exchanges else "") or ""
    sic = sub.get("sic", "")
    sic_desc = sub.get("sicDescription", "")

    recent = sub.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    filing_dates = recent.get("filingDate", [])

    prior_reports = [
        (frm, dt)
        for frm, dt in zip(forms, filing_dates)
        if frm in ("10-K", "10-Q", "20-F", "10-K/A", "20-F/A") and dt < "2026-01-01"
    ]

    is_fund = (
        sic in ("6722", "6726")
        or "fund" in comp_name.lower()
        or "etf" in comp_name.lower()
    )
    is_spac = (
        sic == "6770"
        or "acquisition" in comp_name.lower()
        or "spac" in comp_name.lower()
    )

    if prior_reports:
        exclusions.append(
            {
                "company_name": comp_name,
                "cik": cik,
                "reason": "FOLLOW_ON",
                "detail": f"Prior periodic reports before 2026: {len(prior_reports)} reports (e.g. {prior_reports[0][0]} on {prior_reports[0][1]})",
            }
        )
    elif any(
        ex in exchange
        for ex in ["American", "Arca", "BATS", "OTC", "PINK", "Other"]
    ):
        exclusions.append(
            {
                "company_name": comp_name,
                "cik": cik,
                "reason": "WRONG_VENUE",
                "detail": f"Listed on {exchange}",
            }
        )
    elif is_fund:
        exclusions.append(
            {
                "company_name": comp_name,
                "cik": cik,
                "reason": "FUND",
                "detail": f"Investment fund/trust (SIC {sic}: {sic_desc})",
            }
        )
    else:
        candidates.append(
            {
                "company_name": comp_name,
                "cik": cik,
                "ticker": ticker,
                "exchange": exchange,
                "sic": sic,
                "sic_desc": sic_desc,
                "is_spac": is_spac,
                "date_filed": item["date_filed"],
                "file_name": item["file_name"],
            }
        )

print(f"Candidates without prior 10-K/10-Q: {len(candidates)}")
print(f"Exclusions logged: {len(exclusions)}")
print("\nSample Candidates:")
for c in candidates[:20]:
    t = c["ticker"] or "NO_TICK"
    ex = c["exchange"] or "NO_EXCH"
    sp = "SPAC" if c["is_spac"] else "OPERATING"
    print(f"{t:8s} | CIK {c['cik']:10s} | {ex:15s} | {sp:10s} | {c['company_name'][:35]}")
