"""Unit tests for pure domain logic modules."""

from datetime import date
from decimal import Decimal

from ipo_ledger.domain.classify import classify_filing
from ipo_ledger.domain.compute import (
    compute_gross,
    recompute_gross_micro_units,
)
from ipo_ledger.domain.gate import evaluate_gate
from ipo_ledger.domain.reconcile import SecondaryCheckValues, reconcile_record


def test_classification_logic() -> None:
    """Verify classification of IPOs, SPACs, and excluded offerings."""
    status, code, is_spac = classify_filing(
        form_type="424B4",
        exchange="NASDAQ GLOBAL SELECT",
        is_direct_listing=False,
        is_de_spac=False,
        is_spac_unit=False,
        is_follow_on=False,
        is_fund_or_etf=False,
        is_priced=True,
        has_prior_public_trading=False,
    )
    assert status == "IPO"
    assert code is None
    assert is_spac is False

    status, code, _ = classify_filing(
        form_type="424B4",
        exchange="NYSE AMERICAN",
        is_direct_listing=False,
        is_de_spac=False,
        is_spac_unit=False,
        is_follow_on=False,
        is_fund_or_etf=False,
        is_priced=True,
        has_prior_public_trading=False,
    )
    assert status == "EXCLUDED"
    assert code == "WRONG_VENUE"

    status, code, _ = classify_filing(
        form_type="424B5",
        exchange="NASDAQ",
        is_direct_listing=False,
        is_de_spac=False,
        is_spac_unit=False,
        is_follow_on=True,
        is_fund_or_etf=False,
        is_priced=True,
        has_prior_public_trading=False,
    )
    assert status == "EXCLUDED"
    assert code == "FOLLOW_ON"


def test_computation_and_recompute() -> None:
    """Verify Decimal gross amount agrees with micro-unit integer recomputation."""
    shares = 12500000
    price = Decimal("22.50")
    primary = compute_gross(shares, price)
    recompute = recompute_gross_micro_units(shares, price)
    assert primary == Decimal("281250000.00")
    assert recompute == primary


def test_reconciliation_greenshoe_detection() -> None:
    """Verify secondary source with greenshoe is detected and logged."""
    sec = SecondaryCheckValues(
        source_name="Secondary Calendar",
        source_url="https://example.com/calendar",
        ticker="TEST",
        exchange="NASDAQ",
        pricing_date=date(2026, 3, 10),
        offer_price=Decimal("20.00"),
        base_shares=11500000,
    )
    status, flags, discrepancies = reconcile_record(
        cik="0001999999",
        primary_ticker="TEST",
        primary_exchange="NASDAQ",
        primary_pricing_date=date(2026, 3, 10),
        primary_offer_price=Decimal("20.00"),
        primary_base_shares=10000000,
        secondary_checks=[sec],
        prospectus_url="https://www.sec.gov/filing.htm",
    )
    assert status == "FLAGGED"
    assert "DISCREPANCY_RESOLVED" in flags
    assert len(discrepancies) == 1
    assert "greenshoe" in discrepancies[0].rationale


def test_gate_evaluation() -> None:
    """Verify Gate returns VERIFIED when all pass and DRAFT_INCOMPLETE when any fails."""
    gate_ok = evaluate_gate(
        run_id="run_1",
        universe_reconciled=True,
        urls_valid=True,
        manual_queue_empty=True,
        calc_audit_passed=True,
        no_duplicates=True,
        crosscheck_complete=True,
    )
    assert gate_ok.verdict == "VERIFIED"
    assert len(gate_ok.blockers) == 0

    gate_fail = evaluate_gate(
        run_id="run_2",
        universe_reconciled=False,
        urls_valid=True,
        manual_queue_empty=True,
        calc_audit_passed=True,
        no_duplicates=True,
        crosscheck_complete=True,
    )
    assert gate_fail.verdict == "DRAFT_INCOMPLETE"
    assert len(gate_fail.blockers) > 0
