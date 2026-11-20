"""Unit tests for Stage S3: Cross-Verification."""

from datetime import date
from decimal import Decimal
from pathlib import Path

from ipo_ledger.adapters.storage import LedgerStorage
from ipo_ledger.domain.reconcile import SecondaryCheckValues
from ipo_ledger.domain.schema import IpoRecordModel
from ipo_ledger.pipeline.crosscheck import StageS3CrossCheck


def test_s3_crosscheck_execution(tmp_path: Path) -> None:
    """Verify S3 performs multi-source matching and generates discrepancy models."""
    db_file = tmp_path / "ledger.sqlite"
    storage = LedgerStorage(db_file)
    s3 = StageS3CrossCheck(storage=storage)

    rec1 = IpoRecordModel(
        cik="0002000001",
        accession_no="0001193125-26-000001",
        company_name="Alpha Tech",
        ticker="ALPH",
        exchange="NASDAQ",
        pricing_date=date(2026, 2, 10),
        offer_price=Decimal("20.00"),
        base_shares=10000000,
        gross_offering_amount=Decimal("200000000.00"),
        form_type="424B4",
        prospectus_url="https://www.sec.gov/doc1.htm",
        status="VERIFIED",
    )

    rec2 = IpoRecordModel(
        cik="0002000002",
        accession_no="0001193125-26-000002",
        company_name="Beta Pharma",
        ticker="BETA",
        exchange="NASDAQ",
        pricing_date=date(2026, 3, 1),
        offer_price=Decimal("15.00"),
        base_shares=5000000,
        gross_offering_amount=Decimal("75000000.00"),
        form_type="424B4",
        prospectus_url="https://www.sec.gov/doc2.htm",
        status="VERIFIED",
    )

    sec_map = {
        "0002000001": [
            SecondaryCheckValues(
                source_name="Nasdaq Calendar",
                source_url="https://nasdaq.com/alph",
                ticker="ALPH",
                exchange="NASDAQ",
                pricing_date=date(2026, 2, 10),
                offer_price=Decimal("20.00"),
                base_shares=10000000,
            )
        ],
        "0002000002": [
            SecondaryCheckValues(
                source_name="Financial Provider",
                source_url="https://provider.com/beta",
                ticker="BETA",
                exchange="NASDAQ",
                pricing_date=date(2026, 3, 1),
                offer_price=Decimal("15.00"),
                base_shares=5750000,
            )
        ],
    }

    out_dir = tmp_path / "stage_s3_out"
    updated, checks, discrepancies = s3.run([rec1, rec2], sec_map, out_dir)

    assert len(updated) == 2
    assert updated[0].status == "VERIFIED"
    assert updated[1].status == "FLAGGED"
    assert "DISCREPANCY_RESOLVED" in updated[1].flag_codes
    assert len(checks) == 2
    assert len(discrepancies) == 1
    assert (out_dir / "cross_checks.json").exists()
    assert (out_dir / "discrepancies.json").exists()
