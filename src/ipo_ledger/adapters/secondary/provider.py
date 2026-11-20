"""Secondary financial data provider adapter (PRD Section 2.3, 3.4)."""

from datetime import date
from decimal import Decimal

from ipo_ledger.domain.reconcile import SecondaryCheckValues


class FinancialProviderAdapter:
    """Adapter for reputable independent financial data providers and press releases."""

    def __init__(self, provider_name: str = "Financial Data Provider") -> None:
        self.provider_name = provider_name

    def build_check_values(
        self,
        ticker: str,
        exchange: str,
        pricing_date: date | None,
        offer_price: Decimal | None,
        base_shares: int | None,
        source_url: str,
    ) -> SecondaryCheckValues:
        """Construct structured SecondaryCheckValues."""
        return SecondaryCheckValues(
            source_name=self.provider_name,
            source_url=source_url,
            ticker=ticker,
            exchange=exchange,
            pricing_date=pricing_date,
            offer_price=offer_price,
            base_shares=base_shares,
        )
