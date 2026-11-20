"""Pure domain reconciliation and conflict resolution logic (PRD Section 3.4)."""

from datetime import date
from decimal import Decimal
from typing import NamedTuple

from ipo_ledger.domain.schema import DiscrepancyModel


class SecondaryCheckValues(NamedTuple):
    """Secondary source values for field-level comparison."""

    source_name: str
    source_url: str
    ticker: str
    exchange: str
    pricing_date: date | None
    offer_price: Decimal | None
    base_shares: int | None


def reconcile_record(
    cik: str,
    primary_ticker: str,
    primary_exchange: str,
    primary_pricing_date: date,
    primary_offer_price: Decimal,
    primary_base_shares: int,
    secondary_checks: list[SecondaryCheckValues],
    prospectus_url: str,
    discrepancy_id_start: int = 1,
) -> tuple[str, list[str], list[DiscrepancyModel]]:
    """Compare primary vs secondary values, apply precedence rules, and emit discrepancies."""
    flags: list[str] = []
    discrepancies: list[DiscrepancyModel] = []
    next_id = discrepancy_id_start

    if not secondary_checks:
        flags.append("SINGLE_SOURCE")
        return "FLAGGED", flags, discrepancies

    all_matched = True
    for sec in secondary_checks:
        if sec.offer_price is not None and sec.offer_price != primary_offer_price:
            all_matched = False
            discrepancies.append(
                DiscrepancyModel(
                    discrepancy_id=next_id,
                    cik=cik,
                    field_name="Offer Price",
                    primary_value=f"${primary_offer_price}",
                    secondary_value=f"${sec.offer_price}",
                    source_urls=f"{prospectus_url} vs {sec.source_url}",
                    resolution=f"${primary_offer_price}",
                    rationale="Primary SEC 424B4 prospectus is authoritative for offer price.",
                    resolver="rule",
                )
            )
            next_id += 1

        if sec.base_shares is not None and sec.base_shares != primary_base_shares:
            all_matched = False
            ratio = Decimal(sec.base_shares) / Decimal(primary_base_shares)
            is_likely_greenshoe = Decimal("1.14") <= ratio <= Decimal("1.16")
            greenshoe_note = (
                " (secondary source included over-allotment/greenshoe)"
                if is_likely_greenshoe
                else ""
            )
            discrepancies.append(
                DiscrepancyModel(
                    discrepancy_id=next_id,
                    cik=cik,
                    field_name="Base Shares Offered",
                    primary_value=f"{primary_base_shares:,}",
                    secondary_value=f"{sec.base_shares:,}{greenshoe_note}",
                    source_urls=f"{prospectus_url} vs {sec.source_url}",
                    resolution=f"{primary_base_shares:,}",
                    rationale=(
                        "Primary prospectus base shares strictly exclude over-allotment"
                        f"{greenshoe_note}."
                    ),
                    resolver="rule",
                )
            )
            next_id += 1

        if sec.pricing_date is not None and sec.pricing_date != primary_pricing_date:
            all_matched = False
            discrepancies.append(
                DiscrepancyModel(
                    discrepancy_id=next_id,
                    cik=cik,
                    field_name="Pricing Date",
                    primary_value=str(primary_pricing_date),
                    secondary_value=str(sec.pricing_date),
                    source_urls=f"{prospectus_url} vs {sec.source_url}",
                    resolution=str(primary_pricing_date),
                    rationale=(
                        "Prospectus pricing date takes precedence over first trade or listing date."
                    ),
                    resolver="rule",
                )
            )
            next_id += 1

    if discrepancies:
        flags.append("DISCREPANCY_RESOLVED")
        return "FLAGGED", flags, discrepancies

    if all_matched:
        return "VERIFIED", flags, discrepancies

    return "FLAGGED", flags, discrepancies
