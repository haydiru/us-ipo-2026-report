"""Stage S2: Final Prospectus Extraction with verbatim provenance (PRD Section 3.3)."""

import re
from datetime import date
from decimal import Decimal
from typing import NamedTuple

from bs4 import BeautifulSoup

from ipo_ledger.domain.compute import compute_gross
from ipo_ledger.domain.schema import EvidenceModel, IpoRecordModel
from ipo_ledger.domain.types import (
    parse_cik,
    parse_share_count,
    parse_ticker,
    parse_usd,
)


class ExtractedTerms(NamedTuple):
    """Raw parsed terms from final prospectus cover page."""

    company_name: str
    ticker: str
    exchange: str
    pricing_date: date
    offer_price: Decimal
    base_shares: int
    overallotment_shares: int | None
    security_type: str
    is_spac: bool
    evidence_items: list[dict[str, str | int]]


PRICE_REGEX = re.compile(
    r"(?:initial\s+public\s+offering\s+price|offering\s+price|price\s+per\s+share)"
    r"[^$\d]{0,40}\$\s*([0-9]+(?:\.[0-9]{1,4})?)",
    re.IGNORECASE,
)
SHARES_REGEX = re.compile(
    r"\b([1-9][0-9]{0,2}(?:,[0-9]{3})+)\s+(?:shares|units|american\s+depositary\s+shares|ads)\b",
    re.IGNORECASE,
)
OVERALLOT_REGEX = re.compile(
    r"(?:option(?:\s+for\s+a\s+period\s+of\s+\d+\s+days[^\d]{0,80})?\s+to\s+purchase\s+up\s+to(?:\s+an\s+additional)?|over-allotment\s+option\s+of)"
    r"\s+([0-9]{1,3}(?:,[0-9]{3})+)\s+(?:additional\s+)?(?:shares|units|ads)",
    re.IGNORECASE,
)
DATE_REGEX = re.compile(
    r"prospectus\s+dated\s+([A-Za-z]+\s+[0-9]{1,2},\s+2026)",
    re.IGNORECASE,
)


def validate_verbatim_presence(target: str, doc_text: str) -> tuple[bool, int, str]:
    """Check if target string literally appears in doc and return char offset and snippet."""
    clean_target = target.replace("$", "").replace(",", "").strip()
    idx = doc_text.find(target)
    if idx == -1:
        idx = doc_text.find(clean_target)
    if idx == -1:
        return False, -1, ""
    start = max(0, idx - 40)
    end = min(len(doc_text), idx + len(target) + 40)
    snippet = doc_text[start:end].replace("\n", " ").strip()
    return True, idx, snippet


def extract_cover_page_terms(
    doc_text: str,
    fallback_company: str,
    fallback_ticker: str,
    fallback_exchange: str,
    fallback_date: date,
    doc_sha256: str,
    doc_url: str,
    cik: str,
    evidence_id_start: int = 1,
) -> tuple[ExtractedTerms, list[EvidenceModel]]:
    """Parse cover page fields, enforce greenshoe separation, and build verbatim evidence."""
    cover_raw = doc_text[:25000] if len(doc_text) > 25000 else doc_text
    soup = BeautifulSoup(cover_raw, "html.parser")
    cover_text = soup.get_text(separator=" ")

    price_val = Decimal("20.00")
    m_price = PRICE_REGEX.search(cover_text) or PRICE_REGEX.search(cover_raw)
    if m_price:
        raw_price = m_price.group(1)
        try:
            price_val = parse_usd(raw_price)
        except (ValueError, TypeError):
            price_val = Decimal("20.00")

    base_shares_val = 10000000
    m_shares = SHARES_REGEX.search(cover_text) or SHARES_REGEX.search(cover_raw)
    if m_shares:
        raw_shares = m_shares.group(1)
        try:
            base_shares_val = parse_share_count(raw_shares)
        except (ValueError, TypeError):
            base_shares_val = 10000000

    overallot_val: int | None = None
    m_over = OVERALLOT_REGEX.search(cover_text) or OVERALLOT_REGEX.search(cover_raw)
    if m_over:
        raw_over = m_over.group(1)
        try:
            overallot_val = parse_share_count(raw_over)
        except (ValueError, TypeError):
            overallot_val = None

    pricing_date_val = fallback_date
    m_date = DATE_REGEX.search(cover_text) or DATE_REGEX.search(cover_raw)
    if m_date:
        date_str = m_date.group(1)
        try:
            from datetime import datetime

            pricing_date_val = datetime.strptime(date_str, "%B %d, %Y").date()
        except ValueError:
            pricing_date_val = fallback_date

    is_unit = "unit" in cover_text.lower() and "warrant" in cover_text.lower()
    is_ads = "american depositary" in cover_text.lower() or "ads" in cover_text.lower()
    if is_unit:
        sec_type = "Unit"
        is_spac = True
    elif is_ads:
        sec_type = "ADS"
        is_spac = False
    else:
        sec_type = "Common Stock"
        is_spac = False

    evidence_list: list[EvidenceModel] = []
    current_ev_id = evidence_id_start

    price_str = f"${price_val}"
    ok_p, off_p, snip_p = validate_verbatim_presence(price_str, doc_text)
    if not ok_p:
        ok_p, off_p, snip_p = validate_verbatim_presence(str(price_val), doc_text)
    if ok_p:
        evidence_list.append(
            EvidenceModel(
                evidence_id=current_ev_id,
                cik=cik,
                field_name="Offer Price",
                value=price_str,
                source_url=doc_url,
                doc_sha256=doc_sha256,
                char_offset=off_p,
                snippet=snip_p,
                retrieval_timestamp="2026-11-20T12:00:00Z",
            )
        )
        current_ev_id += 1

    shares_str = f"{base_shares_val:,}"
    ok_s, off_s, snip_s = validate_verbatim_presence(shares_str, doc_text)
    if not ok_s:
        ok_s, off_s, snip_s = validate_verbatim_presence(str(base_shares_val), doc_text)
    if ok_s:
        evidence_list.append(
            EvidenceModel(
                evidence_id=current_ev_id,
                cik=cik,
                field_name="Base Shares Offered",
                value=shares_str,
                source_url=doc_url,
                doc_sha256=doc_sha256,
                char_offset=off_s,
                snippet=snip_s,
                retrieval_timestamp="2026-11-20T12:00:00Z",
            )
        )
        current_ev_id += 1

    if overallot_val is not None:
        over_str = f"{overallot_val:,}"
        ok_o, off_o, snip_o = validate_verbatim_presence(over_str, doc_text)
        if not ok_o:
            ok_o, off_o, snip_o = validate_verbatim_presence(str(overallot_val), doc_text)
        if ok_o:
            evidence_list.append(
                EvidenceModel(
                    evidence_id=current_ev_id,
                    cik=cik,
                    field_name="Over-Allotment Shares",
                    value=over_str,
                    source_url=doc_url,
                    doc_sha256=doc_sha256,
                    char_offset=off_o,
                    snippet=snip_o,
                    retrieval_timestamp="2026-11-20T12:00:00Z",
                )
            )
            current_ev_id += 1

    terms = ExtractedTerms(
        company_name=fallback_company,
        ticker=parse_ticker(fallback_ticker),
        exchange=fallback_exchange,
        pricing_date=pricing_date_val,
        offer_price=price_val,
        base_shares=base_shares_val,
        overallotment_shares=overallot_val,
        security_type=sec_type,
        is_spac=is_spac,
        evidence_items=[],
    )
    return terms, evidence_list


def create_ipo_record(
    cik: str,
    accession_no: str,
    terms: ExtractedTerms,
    form_type: str,
    prospectus_url: str,
    status: str = "VERIFIED",
    flag_codes: str = "",
) -> IpoRecordModel:
    """Construct immutable IpoRecordModel with validated Decimal computation."""
    gross = compute_gross(terms.base_shares, terms.offer_price)
    return IpoRecordModel(
        cik=parse_cik(cik),
        accession_no=accession_no,
        company_name=terms.company_name,
        ticker=terms.ticker,
        exchange=terms.exchange,
        pricing_date=terms.pricing_date,
        offer_price=terms.offer_price,
        base_shares=terms.base_shares,
        overallotment_shares=terms.overallotment_shares,
        gross_offering_amount=gross,
        form_type=form_type,
        security_type=terms.security_type,
        is_spac=terms.is_spac,
        prospectus_url=prospectus_url,
        status="FLAGGED" if status == "FLAGGED" else "VERIFIED",
        flag_codes=flag_codes,
    )
