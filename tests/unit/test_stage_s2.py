"""Unit tests for Stage S2: Final Prospectus Extraction."""

from datetime import date
from decimal import Decimal

from ipo_ledger.pipeline.extract import (
    create_ipo_record,
    extract_cover_page_terms,
    validate_verbatim_presence,
)

SAMPLE_PROSPECTUS_COVER = """
PROSPECTUS
15,000,000 Shares
Common Stock
Initial public offering price per share: $24.00
We have granted the underwriters an option to purchase up to an additional 2,250,000 shares
to cover over-allotments.
Prospectus dated March 15, 2026
"""


def test_extract_cover_page_and_greenshoe_separation() -> None:
    """Verify base shares exclude greenshoe and pricing/shares are parsed."""
    terms, evidence = extract_cover_page_terms(
        doc_text=SAMPLE_PROSPECTUS_COVER,
        fallback_company="Nova Bio Inc",
        fallback_ticker="NVBO",
        fallback_exchange="NASDAQ",
        fallback_date=date(2026, 3, 1),
        doc_sha256="abc123sha",
        doc_url="https://www.sec.gov/doc.htm",
        cik="0002000005",
    )
    assert terms.offer_price == Decimal("24.00")
    assert terms.base_shares == 15000000
    assert terms.overallotment_shares == 2250000
    assert terms.base_shares != terms.base_shares + (terms.overallotment_shares or 0)
    assert terms.pricing_date == date(2026, 3, 15)
    assert len(evidence) >= 2


def test_verbatim_presence() -> None:
    """Verify verbatim text presence and offset calculation."""
    ok, offset, snippet = validate_verbatim_presence("$24.00", SAMPLE_PROSPECTUS_COVER)
    assert ok is True
    assert offset > 0
    assert "$24.00" in snippet


def test_create_ipo_record() -> None:
    """Verify IpoRecordModel creation with validated Gross calculation."""
    terms, _ = extract_cover_page_terms(
        doc_text=SAMPLE_PROSPECTUS_COVER,
        fallback_company="Nova Bio Inc",
        fallback_ticker="NVBO",
        fallback_exchange="NASDAQ",
        fallback_date=date(2026, 3, 15),
        doc_sha256="abc123sha",
        doc_url="https://www.sec.gov/doc.htm",
        cik="0002000005",
    )
    rec = create_ipo_record(
        cik="0002000005",
        accession_no="0001193125-26-000005",
        terms=terms,
        form_type="424B4",
        prospectus_url="https://www.sec.gov/doc.htm",
    )
    assert rec.gross_offering_amount == Decimal("360000000.00")
    assert rec.status == "VERIFIED"
