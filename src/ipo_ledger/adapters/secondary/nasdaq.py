"""Secondary source adapter for Nasdaq IPO calendar (PRD Section 2.3, 3.4)."""

from datetime import date
from decimal import Decimal

from ipo_ledger.domain.reconcile import SecondaryCheckValues


class NasdaqCalendarAdapter:
    """Adapter querying and structuring Nasdaq IPO calendar data."""

    def __init__(self, user_agent: str) -> None:
        self.user_agent = user_agent

    def build_check_values(
        self,
        ticker: str,
        company_name: str,
        pricing_date: date | None,
        offer_price: Decimal | None,
        base_shares: int | None,
        source_url: str = "https://www.nasdaq.com/market-activity/ipos",
    ) -> SecondaryCheckValues:
        """Construct structured SecondaryCheckValues for Nasdaq calendar."""
        return SecondaryCheckValues(
            source_name="Nasdaq IPO Calendar",
            source_url=source_url,
            ticker=ticker,
            exchange="NASDAQ",
            pricing_date=pricing_date,
            offer_price=offer_price,
            base_shares=base_shares,
        )
