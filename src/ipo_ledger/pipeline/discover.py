"""Stage S1: Universe Discovery from EDGAR form index and calendars (PRD Section 3.2)."""

import csv
import json
from datetime import date
from pathlib import Path
from typing import Any

from ipo_ledger.adapters.edgar import EdgarUrls
from ipo_ledger.adapters.storage import LedgerStorage
from ipo_ledger.domain.classify import classify_filing
from ipo_ledger.domain.schema import CandidateModel, ExclusionModel


class StageS1Discover:
    """Stage S1 orchestrator for universe discovery and calendar reconciliation."""

    def __init__(self, run_id: str, storage: LedgerStorage) -> None:
        self.run_id = run_id
        self.storage = storage

    def parse_index_lines(self, index_text: str) -> list[dict[str, str]]:
        """Parse EDGAR fixed-width form.idx text lines."""
        records: list[dict[str, str]] = []
        in_data = False
        for line in index_text.splitlines():
            if not in_data:
                if line.startswith("---"):
                    in_data = True
                continue
            if not line.strip() or len(line) < 103:
                continue
            records.append(
                {
                    "form_type": line[:12].strip(),
                    "company_name": line[12:74].strip(),
                    "cik": line[74:86].strip(),
                    "date_filed": line[86:102].strip(),
                    "file_name": line[102:].strip(),
                }
            )
        return records

    def run_on_feed(
        self,
        filing_items: list[dict[str, Any]],
        calendar_items: list[dict[str, str]],
        output_dir: Path,
    ) -> tuple[list[CandidateModel], list[ExclusionModel], list[dict[str, str]]]:
        """Process discovery feed, classify, reconcile against calendars, and save outputs."""
        output_dir.mkdir(parents=True, exist_ok=True)
        candidates: list[CandidateModel] = []
        exclusions: list[ExclusionModel] = []
        seen_accessions: set[str] = set()

        for item in filing_items:
            acc = str(item["accession_no"])
            if acc in seen_accessions:
                continue
            seen_accessions.add(acc)

            form_type = str(item.get("form_type", "424B4"))
            exchange = str(item.get("exchange", "NASDAQ"))
            is_direct = bool(item.get("is_direct_listing", False))
            is_de_spac = bool(item.get("is_de_spac", False))
            is_spac_unit = bool(item.get("is_spac_unit", False))
            is_follow_on = bool(item.get("is_follow_on", False))
            is_fund = bool(item.get("is_fund_or_etf", False))
            is_priced = bool(item.get("is_priced", True))
            has_prior = bool(item.get("has_prior_public_trading", False))

            verdict, reason, _ = classify_filing(
                form_type=form_type,
                exchange=exchange,
                is_direct_listing=is_direct,
                is_de_spac=is_de_spac,
                is_spac_unit=is_spac_unit,
                is_follow_on=is_follow_on,
                is_fund_or_etf=is_fund,
                is_priced=is_priced,
                has_prior_public_trading=has_prior,
            )

            filing_date_val = item.get("filing_date")
            if isinstance(filing_date_val, str):
                fdate = date.fromisoformat(filing_date_val)
            elif isinstance(filing_date_val, date):
                fdate = filing_date_val
            else:
                fdate = date(2026, 1, 1)

            evidence_url = str(item.get("evidence_url", EdgarUrls.fallback_filing_url(acc)))

            if verdict == "IPO":
                cand = CandidateModel(
                    accession_no=acc,
                    run_id=self.run_id,
                    cik=str(item["cik"]).zfill(10),
                    company_name=str(item["company_name"]),
                    form_type=form_type,
                    filing_date=fdate,
                    classification="IPO",
                )
                candidates.append(cand)
            else:
                exc = ExclusionModel(
                    accession_no=acc,
                    run_id=self.run_id,
                    company_name=str(item["company_name"]),
                    reason_code=reason if reason else "OTHER",  # type: ignore[arg-type]
                    evidence_url=evidence_url,
                )
                exclusions.append(exc)

        candidate_tickers = {
            str(item.get("ticker", "")).upper() for item in filing_items if item.get("ticker")
        }
        unmatched_calendar: list[dict[str, str]] = []
        for cal in calendar_items:
            cal_ticker = cal.get("ticker", "").upper()
            if cal_ticker and cal_ticker not in candidate_tickers:
                unmatched_calendar.append(cal)

        self.storage.save_candidates(candidates)
        self.storage.save_exclusions(exclusions)

        cand_path = output_dir / "candidates.json"
        cand_path.write_text(
            json.dumps([c.model_dump(mode="json") for c in candidates], indent=2),
            encoding="utf-8",
        )

        exc_path = output_dir / "exclusions.csv"
        with exc_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Accession No.", "Company", "Reason Code", "Evidence Link"])
            for exc in exclusions:
                writer.writerow(
                    [
                        exc.accession_no,
                        exc.company_name,
                        exc.reason_code,
                        exc.evidence_url,
                    ]
                )

        unmatched_path = output_dir / "unmatched_calendar.csv"
        with unmatched_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Ticker", "Company", "Pricing Date", "Exchange", "Status"])
            for u in unmatched_calendar:
                writer.writerow(
                    [
                        u.get("ticker", ""),
                        u.get("company", ""),
                        u.get("pricing_date", ""),
                        u.get("exchange", ""),
                        u.get("status", "UNMATCHED"),
                    ]
                )

        return candidates, exclusions, unmatched_calendar
