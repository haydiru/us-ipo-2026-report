"""Pure domain classification logic for IPOs and exclusions (PRD Section 3.2)."""

from typing import Literal

EXCLUDED_VENUES = {
    "NYSE AMERICAN",
    "NYSE ARCA",
    "BATS",
    "OTC",
    "OTCQX",
    "OTCQB",
    "PINK",
}

QUALIFYING_EXCHANGES = {
    "NASDAQ",
    "NASDAQ GLOBAL SELECT",
    "NASDAQ GLOBAL MARKET",
    "NASDAQ CAPITAL MARKET",
    "NYSE",
    "NEW YORK STOCK EXCHANGE",
}

ClassificationVerdict = tuple[
    Literal["IPO", "EXCLUDED"],
    str | None,
    bool,
]


def classify_filing(
    form_type: str,
    exchange: str,
    is_direct_listing: bool,
    is_de_spac: bool,
    is_spac_unit: bool,
    is_follow_on: bool,
    is_fund_or_etf: bool,
    is_priced: bool,
    has_prior_public_trading: bool,
) -> ClassificationVerdict:
    """Classify a filing into qualifying IPO or an exclusion reason code."""
    cleaned_form = form_type.strip().upper()
    if cleaned_form not in {"424B4", "424B1"}:
        return "EXCLUDED", "FOLLOW_ON", False

    if is_follow_on or has_prior_public_trading:
        return "EXCLUDED", "FOLLOW_ON", False

    if is_direct_listing:
        return "EXCLUDED", "DIRECT_LISTING", False

    if is_de_spac:
        return "EXCLUDED", "DE_SPAC", False

    if is_fund_or_etf:
        return "EXCLUDED", "FUND", False

    cleaned_venue = exchange.strip().upper()
    if any(venue in cleaned_venue for venue in EXCLUDED_VENUES):
        return "EXCLUDED", "WRONG_VENUE", False

    if not any(venue in cleaned_venue for venue in QUALIFYING_EXCHANGES):
        return "EXCLUDED", "WRONG_VENUE", False

    if not is_priced:
        return "EXCLUDED", "UNPRICED", False

    return "IPO", None, is_spac_unit
