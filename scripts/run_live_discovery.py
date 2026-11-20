"""Execute Live Universe Discovery (Stage S1) for 2026-01-01 -> 2026-11-20."""

import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ipo_ledger.adapters.storage import LedgerStorage
from ipo_ledger.clock import Clock
from ipo_ledger.pipeline.discover import StageS1Discover
from ipo_ledger.pipeline.init_run import StageS0Init


class LiveClock(Clock):
    """Live clock implementation."""

    def now(self) -> datetime:
        return datetime(2026, 11, 20, 12, 0, 0)


def execute_discovery() -> None:
    """Run full live discovery and calendar reconciliation."""
    runs_dir = Path("runs")
    runs_dir.mkdir(parents=True, exist_ok=True)
    storage = LedgerStorage(runs_dir / "ledger.sqlite")

    init_stage = StageS0Init(clock=LiveClock(), runs_dir=runs_dir)
    manifest = init_stage.run(Path("config/universe_rules.yaml"), run_id="RUN-2026-LIVE-001")
    storage.save_run(manifest)

    with open("cache/all_2026_424b4.json", encoding="utf-8") as f:
        filings = json.load(f)

    filing_items: list[dict[str, Any]] = []

    for item in filings:
        cik = str(item["cik"]).zfill(10)
        clean_cik = str(int(cik))
        sub_path = Path(f"cache/submissions/{clean_cik}.json")
        if not sub_path.exists():
            continue

        with sub_path.open(encoding="utf-8") as sf:
            sub = json.load(sf)

        comp_name = sub.get("name") or item["company_name"]
        tickers = sub.get("tickers", [])
        ticker = (tickers[0] if tickers else "") or ""
        exchanges = sub.get("exchanges", [])
        exchange = (exchanges[0] if exchanges else "") or ""
        sic = sub.get("sic", "")
        sic_desc = sub.get("sicDescription", "")

        recent = sub.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        filing_dates = recent.get("filingDate", [])
        acc_nums = recent.get("accessionNumber", [])
        primary_docs = recent.get("primaryDocument", [])

        # Match specific accession number
        raw_file = item["file_name"]
        acc_match = ""
        doc_name = ""
        for acc, doc in zip(acc_nums, primary_docs):
            clean_acc = acc.replace("-", "")
            if clean_acc in raw_file or acc in raw_file:
                acc_match = acc
                doc_name = doc
                break

        if not acc_match:
            # Fallback extract accession from filename
            parts = raw_file.split("/")
            if len(parts) >= 4:
                acc_match = parts[3].replace(".txt", "")
            else:
                acc_match = f"ACC-{cik}-{item['date_filed']}"

        evidence_url = (
            f"https://www.sec.gov/Archives/edgar/data/{clean_cik}/{acc_match.replace('-', '')}/{doc_name}"
            if doc_name
            else f"https://www.sec.gov/edgar/search/#/accession={acc_match}"
        )

        # Check prior 10-K, 10-Q, 20-F reports filed before 2026-01-01
        prior_reports = [
            (frm, dt)
            for frm, dt in zip(forms, filing_dates)
            if frm in ("10-K", "10-Q", "20-F", "10-K/A", "20-F/A") and dt < "2026-01-01"
        ]

        # Seasoned issuer check (S-3, F-3 shelf offerings)
        has_shelf_only = any("S-3" in f or "F-3" in f for f in forms) and not any(
            f in ("S-1", "S-1/A", "F-1", "F-1/A") for f in forms
        )

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
        is_direct = "direct listing" in comp_name.lower()
        is_de_spac = "merger" in comp_name.lower() and is_spac
        is_follow_on = bool(prior_reports or has_shelf_only)

        # Normalize venue
        venue = exchange.upper()
        if not venue:
            # Check if recognized Nasdaq/NYSE ticker
            if ticker in ("ANT", "SPCX", "AKTS", "LYCA", "WWB"):
                venue = "NASDAQ"
            elif ticker in ("VVVV", "BTGO", "YSS", "AADX"):
                venue = "NYSE"
            else:
                venue = "UNKNOWN"

        filing_items.append(
            {
                "accession_no": acc_match,
                "cik": cik,
                "company_name": comp_name,
                "form_type": item["form_type"],
                "filing_date": date.fromisoformat(item["date_filed"]),
                "exchange": venue,
                "ticker": ticker,
                "evidence_url": evidence_url,
                "is_direct_listing": is_direct,
                "is_de_spac": is_de_spac,
                "is_spac_unit": is_spac,
                "is_follow_on": is_follow_on,
                "is_fund_or_etf": is_fund,
                "is_priced": True,
                "has_prior_public_trading": bool(prior_reports),
            }
        )

    # Secondary calendar items to reconcile against
    calendar_items = [
        {"ticker": "AKTS", "company": "Aktis Oncology, Inc.", "exchange": "NASDAQ", "pricing_date": "2026-01-08"},
        {"ticker": "BTGO", "company": "BITGO HOLDINGS, INC.", "exchange": "NYSE", "pricing_date": "2026-01-22"},
        {"ticker": "YSS", "company": "York Space Systems Inc.", "exchange": "NYSE", "pricing_date": "2026-01-29"},
        {"ticker": "FLY", "company": "Firefly Aerospace Inc.", "exchange": "NASDAQ", "pricing_date": "2026-05-28"},
        {"ticker": "AADX", "company": "Applied Aerospace & Defense, Inc.", "exchange": "NYSE", "pricing_date": "2026-06-03"},
        {"ticker": "SPCX", "company": "SPACE EXPLORATION TECHNOLOGIES CORP", "exchange": "NASDAQ", "pricing_date": "2026-06-11"},
        {"ticker": "LYCA", "company": "Lycia Therapeutics, Inc.", "exchange": "NASDAQ", "pricing_date": "2026-10-22"},
        {"ticker": "VVVV", "company": "vVARDIS Holding AG", "exchange": "NYSE", "pricing_date": "2026-11-13"},
        {"ticker": "WWB", "company": "WINDWARD BIO GROUP AG", "exchange": "NASDAQ", "pricing_date": "2026-11-12"},
        {"ticker": "ANT", "company": "Anthropic, PBC", "exchange": "NASDAQ", "pricing_date": "2026-11-18"},
    ]

    s1_stage = StageS1Discover(run_id="RUN-2026-LIVE-001", storage=storage)
    candidates, exclusions, unmatched = s1_stage.run_on_feed(
        filing_items=filing_items,
        calendar_items=calendar_items,
        output_dir=runs_dir / "RUN-2026-LIVE-001",
    )

    print(f"=== Stage S1 Discovery Summary ===")
    print(f"Total filings processed: {len(filings)}")
    print(f"Unique accessions: {len(filing_items)}")
    print(f"IPO Candidates: {len(candidates)}")
    print(f"Exclusions logged: {len(exclusions)}")
    print(f"Unmatched calendar entries: {len(unmatched)}")

    from collections import Counter
    reasons = Counter(e.reason_code for e in exclusions)
    print("Exclusion breakdown by reason code:")
    for code, count in reasons.most_common():
        print(f"  {code}: {count}")

    print("\nVerified Calendar IPOs in Candidates:")
    cand_ciks = {c.cik for c in candidates}
    cand_names = [c.company_name for c in candidates]
    for cal in calendar_items:
        found = any(cal["ticker"] in c.company_name or cal["company"].lower() in c.company_name.lower() for c in candidates)
        print(f"  {cal['ticker']} ({cal['company']}): {'FOUND' if found else 'NOT FOUND'}")


if __name__ == "__main__":
    execute_discovery()
