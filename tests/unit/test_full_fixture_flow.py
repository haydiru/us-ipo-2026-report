"""End-to-end integration test of Stages S0->S6 on recorded test fixtures."""

from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

from ipo_ledger.adapters.storage import LedgerStorage
from ipo_ledger.clock import FrozenClock
from ipo_ledger.domain.reconcile import SecondaryCheckValues
from ipo_ledger.pipeline.audit import StageS4Audit
from ipo_ledger.pipeline.build import StageS5Build
from ipo_ledger.pipeline.crosscheck import StageS3CrossCheck
from ipo_ledger.pipeline.discover import StageS1Discover
from ipo_ledger.pipeline.extract import create_ipo_record, extract_cover_page_terms
from ipo_ledger.pipeline.gate import StageS6Gate
from ipo_ledger.pipeline.init_run import StageS0Init


def test_full_flow_on_fixtures(tmp_path: Path) -> None:
    """Execute complete S0 through S6 pipeline flow on fixtures."""
    clock = FrozenClock(datetime(2026, 11, 20, 12, 0, 0, tzinfo=UTC))
    runs_dir = tmp_path / "runs"

    import yaml

    cfg_data = {
        "version": "1.0",
        "as_of_date": "2026-11-20",
        "window_start": "2026-01-01",
        "window_end": "2026-11-20",
        "exchanges": {"included": ["NASDAQ", "NYSE"], "excluded": ["OTC"]},
        "offerings": {"direct_listings": False, "spac_mergers": False},
        "rate_limits": {"sec_user_agent": "Agent research@test.internal"},
    }
    cfg_file = tmp_path / "rules.yaml"
    cfg_file.write_text(yaml.dump(cfg_data), encoding="utf-8")

    # S0
    s0 = StageS0Init(clock=clock, runs_dir=runs_dir)
    manifest = s0.run(config_path=cfg_file, run_id="run_fixture_flow")
    run_dir = runs_dir / manifest.run_id
    storage = LedgerStorage(run_dir / "ledger.sqlite")

    # S1
    s1 = StageS1Discover(run_id=manifest.run_id, storage=storage)
    filings = [
        {
            "accession_no": "0001193125-26-000101",
            "cik": "2000101",
            "company_name": "Fixture Tech Inc",
            "ticker": "FTCH",
            "form_type": "424B4",
            "exchange": "NASDAQ GLOBAL SELECT",
            "filing_date": date(2026, 3, 10),
            "is_priced": True,
        }
    ]
    calendars = [{"ticker": "FTCH", "company": "Fixture Tech Inc", "pricing_date": "2026-03-10"}]
    candidates, exclusions, unmatched = s1.run_on_feed(filings, calendars, run_dir)
    assert len(candidates) == 1
    assert len(unmatched) == 0

    # S2
    sample_doc = """
    PROSPECTUS
    10,000,000 Shares
    Initial public offering price per share: $25.00
    We have granted the underwriters an option to purchase up to 1,500,000 additional shares.
    Prospectus dated March 10, 2026
    """
    cand = candidates[0]
    terms, evidence = extract_cover_page_terms(
        doc_text=sample_doc,
        fallback_company=cand.company_name,
        fallback_ticker="FTCH",
        fallback_exchange="NASDAQ GLOBAL SELECT",
        fallback_date=cand.filing_date,
        doc_sha256="sha101",
        doc_url="https://www.sec.gov/Archives/edgar/data/2000101/000119312526000101/doc.htm",
        cik=cand.cik,
    )
    rec = create_ipo_record(
        cik=cand.cik,
        accession_no=cand.accession_no,
        terms=terms,
        form_type="424B4",
        prospectus_url="https://www.sec.gov/Archives/edgar/data/2000101/000119312526000101/doc.htm",
    )
    storage.save_evidence(evidence)

    # S3
    s3 = StageS3CrossCheck(storage=storage)
    sec_map = {
        cand.cik: [
            SecondaryCheckValues(
                source_name="Nasdaq Calendar",
                source_url="https://nasdaq.com/ftch",
                ticker="FTCH",
                exchange="NASDAQ GLOBAL SELECT",
                pricing_date=date(2026, 3, 10),
                offer_price=Decimal("25.00"),
                base_shares=10000000,
            )
        ]
    }
    updated_records, _checks, discrepancies = s3.run([rec], sec_map, run_dir)
    assert updated_records[0].status == "VERIFIED"

    # S4
    s4 = StageS4Audit(storage=storage)
    audit_passed, _results, metrics, duplicates = s4.run(updated_records, run_dir)
    assert audit_passed is True

    # S5
    s5 = StageS5Build()
    meta = {
        "Run ID": manifest.run_id,
        "AS_OF_DATE": "2026-11-20",
        "Rule Hash": manifest.rule_hash,
        "Status": "VERIFIED",
    }
    out_xlsx = run_dir / "us_ipo_report_2026.xlsx"
    s5.run(
        output_xlsx_path=out_xlsx,
        records=updated_records,
        discrepancies=discrepancies,
        exclusions=exclusions,
        evidence=evidence,
        metadata=meta,
        audit_summary_metrics=metrics,
    )
    assert out_xlsx.exists()

    # S6
    s6 = StageS6Gate(storage=storage)
    gate_res = s6.run(
        run_id=manifest.run_id,
        records=updated_records,
        unmatched_calendar_rows=unmatched,
        manual_queue_count=0,
        calc_audit_passed=audit_passed,
        duplicate_count=len(duplicates),
        output_dir=run_dir,
    )
    assert gate_res.verdict == "VERIFIED"
