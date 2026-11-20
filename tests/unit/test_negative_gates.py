"""Unit tests verifying that illegal operations and footguns are strictly rejected."""

from decimal import Decimal

import pytest

from ipo_ledger.domain.types import (
    parse_cik,
    parse_share_count,
    parse_ticker,
    parse_usd,
    parse_usd_amount,
)


def test_reject_float_in_usd_price() -> None:
    """Ensure float offer price is rejected with TypeError."""
    with pytest.raises(TypeError, match="Float values are strictly forbidden"):
        parse_usd(15.5)  # type: ignore[arg-type]


def test_reject_float_in_usd_amount() -> None:
    """Ensure float gross amount is rejected with TypeError."""
    with pytest.raises(TypeError, match="Float values are strictly forbidden"):
        parse_usd_amount(1500000.50)  # type: ignore[arg-type]


def test_reject_float_in_share_count() -> None:
    """Ensure float share count is rejected with TypeError."""
    with pytest.raises(TypeError, match="Float values are forbidden"):
        parse_share_count(1000.5)  # type: ignore[arg-type]


def test_reject_negative_or_zero_values() -> None:
    """Ensure negative or zero prices/shares are rejected."""
    with pytest.raises(ValueError):
        parse_usd("0.00")
    with pytest.raises(ValueError):
        parse_usd("-5.00")
    with pytest.raises(ValueError):
        parse_share_count(0)
    with pytest.raises(ValueError):
        parse_share_count(-100)


def test_valid_parsing() -> None:
    """Ensure correct parsing and types for valid inputs."""
    assert parse_cik("320193") == "0000320193"
    assert parse_ticker("aapl") == "AAPL"
    assert parse_usd("$18.50") == Decimal("18.50")
    assert parse_share_count("1,500,000") == 1500000
    assert parse_usd_amount("$27,750,000.00") == Decimal("27750000.00")
