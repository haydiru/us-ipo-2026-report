"""Unit tests for secondary source adapters."""

from datetime import date
from decimal import Decimal

from ipo_ledger.adapters.secondary.nasdaq import NasdaqCalendarAdapter
from ipo_ledger.adapters.secondary.provider import FinancialProviderAdapter


def test_nasdaq_adapter() -> None:
    """Verify Nasdaq adapter constructs valid SecondaryCheckValues."""
    adapter = NasdaqCalendarAdapter(user_agent="Agent")
    check = adapter.build_check_values(
        ticker="DEMO",
        company_name="Demo Corp",
        pricing_date=date(2026, 4, 1),
        offer_price=Decimal("18.00"),
        base_shares=6000000,
    )
    assert check.source_name == "Nasdaq IPO Calendar"
    assert check.ticker == "DEMO"
    assert check.offer_price == Decimal("18.00")
    assert check.base_shares == 6000000


def test_provider_adapter() -> None:
    """Verify financial provider adapter structures secondary data."""
    adapter = FinancialProviderAdapter("Bloomberg/PR")
    check = adapter.build_check_values(
        ticker="DEMO",
        exchange="NYSE",
        pricing_date=date(2026, 4, 1),
        offer_price=Decimal("18.00"),
        base_shares=6000000,
        source_url="https://example.com/pr",
    )
    assert check.source_name == "Bloomberg/PR"
    assert check.exchange == "NYSE"
