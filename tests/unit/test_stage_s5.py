"""Unit tests for Stage S5: Assembly and CLI orchestration."""

from datetime import date
from decimal import Decimal
from pathlib import Path

from ipo_ledger.domain.schema import IpoRecordModel
from ipo_ledger.pipeline.build import StageS5Build


def test_s5_build_execution(tmp_path: Path) -> None:
    """Verify S5 builds .xlsx workbook adhering to 6-sheet schema."""
    s5 = StageS5Build()
    out_file = tmp_path / "test_out.xlsx"
    records = [
        IpoRecordModel(
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
    ]
    meta = {"Run ID": "test_s5", "AS_OF_DATE": "2026-11-20"}
    metrics = {"total_ipos_all": 1, "gross_all": Decimal("200000000.00")}

    res = s5.run(
        output_xlsx_path=out_file,
        records=records,
        discrepancies=[],
        exclusions=[],
        evidence=[],
        metadata=meta,
        audit_summary_metrics=metrics,
    )
    assert res.exists()
    assert res.stat().st_size > 4000
