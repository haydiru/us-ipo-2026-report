"""Test and prototype generator for Phase 1 Static Workbook Prototype."""

from datetime import date
from decimal import Decimal
from pathlib import Path

from ipo_ledger.domain.schema import (
    DiscrepancyModel,
    EvidenceModel,
    ExclusionModel,
    IpoRecordModel,
)
from ipo_ledger.report.workbook import build_workbook


def create_sample_dataset() -> tuple[
    list[IpoRecordModel],
    list[DiscrepancyModel],
    list[ExclusionModel],
    list[EvidenceModel],
    dict[str, str],
    dict[str, object],
]:
    """Build representative dataset of 5 rows covering diverse offering structures."""
    records = [
        IpoRecordModel(
            cik="0002011001",
            accession_no="0001193125-26-001001",
            company_name="Apex Quantum Dynamics Inc.",
            ticker="APXD",
            exchange="NASDAQ GLOBAL SELECT",
            pricing_date=date(2026, 2, 12),
            offer_price=Decimal("22.00"),
            base_shares=12500000,
            overallotment_shares=1875000,
            gross_offering_amount=Decimal("275000000.00"),
            form_type="424B4",
            security_type="Common Stock",
            is_spac=False,
            prospectus_url="https://www.sec.gov/Archives/edgar/data/0002011001/000119312526001001/d424b4.htm",
            status="VERIFIED",
            flag_codes="",
        ),
        IpoRecordModel(
            cik="0002022002",
            accession_no="0000950170-26-002002",
            company_name="Helios BioTherapeutics Corp.",
            ticker="HLTX",
            exchange="NASDAQ GLOBAL MARKET",
            pricing_date=date(2026, 5, 20),
            offer_price=Decimal("17.00"),
            base_shares=8000000,
            overallotment_shares=1200000,
            gross_offering_amount=Decimal("136000000.00"),
            form_type="424B4",
            security_type="Common Stock",
            is_spac=False,
            prospectus_url="https://www.sec.gov/Archives/edgar/data/0002022002/000095017026002002/prospectus.htm",
            status="VERIFIED",
            flag_codes="",
        ),
        IpoRecordModel(
            cik="0002033003",
            accession_no="0001104659-26-003003",
            company_name="Vanguard Horizons Acquisition Corp.",
            ticker="VHACU",
            exchange="NASDAQ CAPITAL MARKET",
            pricing_date=date(2026, 7, 15),
            offer_price=Decimal("10.00"),
            base_shares=25000000,
            overallotment_shares=3750000,
            gross_offering_amount=Decimal("250000000.00"),
            form_type="424B4",
            security_type="Unit",
            is_spac=True,
            prospectus_url="https://www.sec.gov/Archives/edgar/data/0002033003/000110465926003003/vhac424b4.htm",
            status="VERIFIED",
            flag_codes="",
        ),
        IpoRecordModel(
            cik="0002044004",
            accession_no="0001140364-26-004004",
            company_name="Nordic Genix AG",
            ticker="NGNX",
            exchange="NEW YORK STOCK EXCHANGE",
            pricing_date=date(2026, 9, 24),
            offer_price=Decimal("19.50"),
            base_shares=10000000,
            overallotment_shares=1500000,
            gross_offering_amount=Decimal("195000000.00"),
            form_type="424B4",
            security_type="ADS",
            is_spac=False,
            prospectus_url="https://www.sec.gov/Archives/edgar/data/0002044004/000114036426004004/form424b4.htm",
            status="VERIFIED",
            flag_codes="",
        ),
        IpoRecordModel(
            cik="0002055005",
            accession_no="0001493152-26-005005",
            company_name="Solaria Clean Infrastructure Inc.",
            ticker="SOLC",
            exchange="NASDAQ GLOBAL MARKET",
            pricing_date=date(2026, 11, 5),
            offer_price=Decimal("14.00"),
            base_shares=6500000,
            overallotment_shares=975000,
            gross_offering_amount=Decimal("91000000.00"),
            form_type="424B4",
            security_type="Common Stock",
            is_spac=False,
            prospectus_url="https://www.sec.gov/Archives/edgar/data/0002055005/000149315226005005/solc424b4.htm",
            status="FLAGGED",
            flag_codes="DISCREPANCY_RESOLVED;SINGLE_SOURCE",
        ),
    ]

    discrepancies = [
        DiscrepancyModel(
            discrepancy_id=1,
            cik="0002055005",
            field_name="Base Shares Offered",
            primary_value="6,500,000",
            secondary_value="7,475,000 (greenshoe inclusive)",
            source_urls="SEC 424B4 vs Secondary IPO Calendar",
            resolution="6,500,000",
            rationale=(
                "Aggregator mistakenly included 975k overallotment option. "
                "Prospectus base shares used."
            ),
            resolver="rule",
        )
    ]

    exclusions = [
        ExclusionModel(
            accession_no="0001193125-26-009001",
            run_id="run_prototype",
            company_name="CyberTech Cloud Systems Corp.",
            reason_code="FOLLOW_ON",
            evidence_url="https://www.sec.gov/Archives/edgar/data/0001500001/000119312526009001/d424b5.htm",
        ),
        ExclusionModel(
            accession_no="0000950170-26-009002",
            run_id="run_prototype",
            company_name="Titan Mobility Holdings LLC",
            reason_code="DE_SPAC",
            evidence_url="https://www.sec.gov/Archives/edgar/data/0001600002/000095017026009002/d8k.htm",
        ),
        ExclusionModel(
            accession_no="0001140364-26-009003",
            run_id="run_prototype",
            company_name="Pacific Gold Mining Royalty Inc.",
            reason_code="WRONG_VENUE",
            evidence_url="https://www.sec.gov/Archives/edgar/data/0001700003/000114036426009003/form424b4.htm",
        ),
    ]

    evidence = [
        EvidenceModel(
            evidence_id=1,
            cik="0002011001",
            field_name="Offer Price",
            value="$22.00",
            source_url="https://www.sec.gov/Archives/edgar/data/0002011001/000119312526001001/d424b4.htm",
            doc_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            char_offset=1420,
            snippet="Initial public offering price per share: $22.00",
            retrieval_timestamp="2026-11-20T12:00:00Z",
        ),
        EvidenceModel(
            evidence_id=2,
            cik="0002011001",
            field_name="Base Shares Offered",
            value="12,500,000",
            source_url="https://www.sec.gov/Archives/edgar/data/0002011001/000119312526001001/d424b4.htm",
            doc_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            char_offset=1510,
            snippet="12,500,000 shares of common stock offered by the company",
            retrieval_timestamp="2026-11-20T12:00:00Z",
        ),
    ]

    metadata = {
        "Run ID": "run_prototype_20261120",
        "AS_OF_DATE": "2026-11-20",
        "Window": "2026-01-01 -> 2026-11-20",
        "Rule Hash": "a1b2c3d4e5f67890",
        "Tool Versions": "Python 3.13, XlsxWriter 3.3.3, Pydantic 2.13.4",
        "EDGAR User-Agent": "IPOLedgerAgent research@ipoledger.internal",
        "Report Status": "PROTOTYPE",
    }

    metrics = {
        "total_ipos_all": 5,
        "total_ipos_ex_spac": 4,
        "gross_all": Decimal("947000000.00"),
        "gross_ex_spac": Decimal("697000000.00"),
    }

    return records, discrepancies, exclusions, evidence, metadata, metrics


def test_generate_and_verify_prototype_workbook(tmp_path: Path) -> None:
    """Generate workbook prototype and verify openpyxl integrity."""
    out_file = tmp_path / "prototype_ipo_report.xlsx"
    records, discrepancies, exclusions, evidence, metadata, metrics = create_sample_dataset()
    build_workbook(
        output_path=out_file,
        records=records,
        discrepancies=discrepancies,
        exclusions=exclusions,
        evidence=evidence,
        metadata=metadata,
        audit_summary_metrics=metrics,
    )
    assert out_file.exists()
    assert out_file.stat().st_size > 5000
