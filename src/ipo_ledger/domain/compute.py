"""Pure calculation and independent arithmetic audit logic (PRD Section 3.5)."""

from decimal import ROUND_HALF_EVEN, Decimal
from typing import NamedTuple

from ipo_ledger.domain.schema import AuditResultModel, IpoRecordModel

CENT = Decimal("0.01")
MICRO_UNITS = 10000


class OfferingTotals(NamedTuple):
    """Aggregate totals verified dual-way."""

    total_records: int
    total_gross_decimal: Decimal
    total_gross_recompute: Decimal
    passed: bool


def compute_gross(base_shares: int, offer_price: Decimal) -> Decimal:
    """Compute Gross Offering Amount using Decimal quantized to cents."""
    raw = Decimal(base_shares) * offer_price
    return raw.quantize(CENT, rounding=ROUND_HALF_EVEN)


def recompute_gross_micro_units(base_shares: int, offer_price: Decimal) -> Decimal:
    """Independent micro-unit integer arithmetic recompute."""
    price_micro = int(
        (offer_price * Decimal(MICRO_UNITS)).to_integral_exact(rounding=ROUND_HALF_EVEN)
    )
    gross_micro = base_shares * price_micro
    gross_int_cents = (gross_micro + 50) // 100
    dollars = gross_int_cents // 100
    cents = gross_int_cents % 100
    return Decimal(f"{dollars}.{cents:02d}")


def audit_record_math(rec: IpoRecordModel) -> AuditResultModel:
    """Independently audit single record gross computation."""
    primary = compute_gross(rec.base_shares, rec.offer_price)
    recompute = recompute_gross_micro_units(rec.base_shares, rec.offer_price)
    delta = abs(primary - recompute)
    passed = (delta == Decimal("0.00")) and (primary == rec.gross_offering_amount)
    return AuditResultModel(
        cik=rec.cik,
        gross_primary=primary,
        gross_recompute=recompute,
        delta=delta,
        passed=passed,
    )


def audit_dataset_math(
    records: list[IpoRecordModel],
) -> tuple[list[AuditResultModel], OfferingTotals]:
    """Audit all records and dual-sum aggregate gross amounts."""
    results: list[AuditResultModel] = []
    total_dec = Decimal("0.00")
    total_micro_int = 0

    for rec in records:
        res = audit_record_math(rec)
        results.append(res)
        total_dec += res.gross_primary
        price_micro = int(
            (rec.offer_price * Decimal(MICRO_UNITS)).to_integral_exact(rounding=ROUND_HALF_EVEN)
        )
        total_micro_int += rec.base_shares * price_micro

    recompute_cents = (total_micro_int + 50) // 100
    recompute_total = Decimal(f"{recompute_cents // 100}.{recompute_cents % 100:02d}")
    all_passed = all(r.passed for r in results) and (total_dec == recompute_total)

    totals = OfferingTotals(
        total_records=len(records),
        total_gross_decimal=total_dec,
        total_gross_recompute=recompute_total,
        passed=all_passed,
    )
    return results, totals


def check_duplicates(records: list[IpoRecordModel]) -> list[str]:
    """Check duplicate CIK or (ticker, pricing_date)."""
    errors: list[str] = []
    seen_ciks: set[str] = set()
    seen_keys: set[tuple[str, str]] = set()

    for rec in records:
        if rec.cik in seen_ciks:
            errors.append(f"Duplicate CIK detected: {rec.cik} ({rec.ticker})")
        seen_ciks.add(rec.cik)

        sec_key = (rec.ticker.upper(), str(rec.pricing_date))
        if sec_key in seen_keys:
            errors.append(f"Duplicate (ticker, pricing_date) detected: {sec_key}")
        seen_keys.add(sec_key)

    return errors
