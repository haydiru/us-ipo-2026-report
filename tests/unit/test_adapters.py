"""Unit tests for cache and storage adapters."""

from datetime import date
from decimal import Decimal
from pathlib import Path

from ipo_ledger.adapters.cache import ContentCache
from ipo_ledger.adapters.storage import LedgerStorage
from ipo_ledger.domain.schema import IpoRecordModel, RunManifestModel


def test_content_cache(tmp_path: Path) -> None:
    """Verify content-addressed cache storage and retrieval."""
    cache = ContentCache(tmp_path)
    sample_bytes = b"Sample EDGAR prospectus raw content"
    sha, path = cache.put(sample_bytes)
    assert cache.has(sha)
    assert cache.get(sha) == sample_bytes
    assert path.name == sha


def test_ledger_storage(tmp_path: Path) -> None:
    """Verify SQLite persistence of run manifests and IPO records."""
    db_file = tmp_path / "ledger.sqlite"
    storage = LedgerStorage(db_file)

    manifest = RunManifestModel(
        run_id="test_run_01",
        as_of_date=date(2026, 11, 20),
        rule_hash="hash123",
        tool_versions={"python": "3.13"},
        edgar_user_agent="Agent research@test",
        status="ready",
        created_at="2026-11-20T12:00:00Z",
    )
    storage.save_run(manifest)

    rec = IpoRecordModel(
        cik="0001000001",
        accession_no="0001193125-26-000001",
        company_name="Alpha Corp",
        ticker="ALPH",
        exchange="NASDAQ",
        pricing_date=date(2026, 3, 1),
        offer_price=Decimal("15.00"),
        base_shares=5000000,
        overallotment_shares=750000,
        gross_offering_amount=Decimal("75000000.00"),
        form_type="424B4",
        security_type="Common Stock",
        is_spac=False,
        prospectus_url="https://www.sec.gov/filing.htm",
        status="VERIFIED",
        flag_codes="",
    )
    storage.save_ipo_records([rec])
    assert db_file.exists()
