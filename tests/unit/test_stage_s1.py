"""Unit tests for Stage S1: Universe Discovery."""

from datetime import date
from pathlib import Path

from ipo_ledger.adapters.storage import LedgerStorage
from ipo_ledger.pipeline.discover import StageS1Discover


def test_s1_discover_and_reconcile(tmp_path: Path) -> None:
    """Verify S1 classifies candidates, logs exclusions, and reconciles calendars."""
    db_file = tmp_path / "ledger.sqlite"
    storage = LedgerStorage(db_file)
    from ipo_ledger.domain.schema import RunManifestModel

    storage.save_run(
        RunManifestModel(
            run_id="run_s1_test",
            as_of_date=date(2026, 11, 20),
            rule_hash="h123",
            tool_versions={},
            edgar_user_agent="Agent",
            status="ready",
            created_at="2026-11-20T12:00:00Z",
        )
    )
    s1 = StageS1Discover(run_id="run_s1_test", storage=storage)

    filing_items = [
        {
            "accession_no": "0001193125-26-000001",
            "cik": "2000001",
            "company_name": "Valid IPO Inc",
            "ticker": "VIPO",
            "form_type": "424B4",
            "exchange": "NASDAQ GLOBAL SELECT",
            "filing_date": date(2026, 2, 1),
            "is_priced": True,
        },
        {
            "accession_no": "0001193125-26-000002",
            "cik": "2000002",
            "company_name": "Follow On Corp",
            "ticker": "FOLO",
            "form_type": "424B5",
            "exchange": "NASDAQ",
            "filing_date": date(2026, 2, 2),
            "is_follow_on": True,
        },
        {
            "accession_no": "0001193125-26-000003",
            "cik": "2000003",
            "company_name": "DeSpac Merger Co",
            "ticker": "DSPM",
            "form_type": "424B4",
            "exchange": "NASDAQ",
            "filing_date": date(2026, 2, 3),
            "is_de_spac": True,
        },
    ]

    calendar_items = [
        {"ticker": "VIPO", "company": "Valid IPO Inc", "pricing_date": "2026-02-01"},
        {"ticker": "GHOST", "company": "Ghost Calendar Entry", "pricing_date": "2026-02-05"},
    ]

    out_dir = tmp_path / "stage_s1_out"
    candidates, exclusions, unmatched = s1.run_on_feed(filing_items, calendar_items, out_dir)

    assert len(candidates) == 1
    assert candidates[0].cik == "0002000001"
    assert len(exclusions) == 2
    assert len(unmatched) == 1
    assert unmatched[0]["ticker"] == "GHOST"
    assert (out_dir / "candidates.json").exists()
    assert (out_dir / "exclusions.csv").exists()
    assert (out_dir / "unmatched_calendar.csv").exists()
