"""Unit tests for Stage S4: Computation & Audit."""

from datetime import date
from decimal import Decimal
from pathlib import Path

from ipo_ledger.adapters.storage import LedgerStorage
from ipo_ledger.domain.schema import IpoRecordModel
from ipo_ledger.pipeline.audit import StageS4Audit


def test_s4_audit_success(tmp_path: Path) -> None:
    """Verify S4 computation and recompute audit pass on valid records."""
    db_file = tmp_path / "ledger.sqlite"
    storage = LedgerStorage(db_file)
    s4 = StageS4Audit(storage=storage)

    records = [
        IpoRecordModel(
            cik="0002000001",
            accession_no="0001193125-26-000001",
            company_name="Apex Corp",
            ticker="APEX",
            exchange="NASDAQ",
            pricing_date=date(2026, 2, 10),
            offer_price=Decimal("20.00"),
            base_shares=10000000,
            gross_offering_amount=Decimal("200000000.00"),
            form_type="424B4",
            prospectus_url="https://www.sec.gov/doc1.htm",
            status="VERIFIED",
        ),
        IpoRecordModel(
            cik="0002000002",
            accession_no="0001193125-26-000002",
            company_name="Apex SPAC Corp",
            ticker="APEXU",
            exchange="NASDAQ",
            pricing_date=date(2026, 2, 15),
            offer_price=Decimal("10.00"),
            base_shares=20000000,
            gross_offering_amount=Decimal("200000000.00"),
            form_type="424B4",
            is_spac=True,
            prospectus_url="https://www.sec.gov/doc2.htm",
            status="VERIFIED",
        ),
    ]

    out_dir = tmp_path / "stage_s4_out"
    passed, results, metrics, duplicates = s4.run(records, out_dir)

    assert passed is True
    assert len(results) == 2
    assert all(r.passed for r in results)
    assert metrics["total_ipos_all"] == 2
    assert metrics["total_ipos_ex_spac"] == 1
    assert metrics["gross_all"] == Decimal("400000000.00")
    assert metrics["gross_ex_spac"] == Decimal("200000000.00")
    assert len(duplicates) == 0
    assert (out_dir / "audit_results.json").exists()
