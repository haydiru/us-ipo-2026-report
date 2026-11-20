"""Branded types and validating constructors for the domain."""

import re
from decimal import Decimal, InvalidOperation
from typing import NewType

Cik = NewType("Cik", str)
AccessionNo = NewType("AccessionNo", str)
Ticker = NewType("Ticker", str)
UsdPerShare = NewType("UsdPerShare", Decimal)
ShareCount = NewType("ShareCount", int)
UsdAmount = NewType("UsdAmount", Decimal)

CIK_PATTERN = re.compile(r"^\d{1,10}$")
ACCESSION_PATTERN = re.compile(r"^\d{10}-\d{2}-\d{6}$")
TICKER_PATTERN = re.compile(r"^[A-Z0-9.-]{1,10}$")


def parse_cik(val: str | int) -> Cik:
    """Validate and zero-pad a CIK to 10 digits."""
    s = str(val).strip()
    if not CIK_PATTERN.match(s):
        raise ValueError(f"Invalid CIK format: {val}")
    return Cik(s.zfill(10))


def parse_accession_no(val: str) -> AccessionNo:
    """Validate standard EDGAR accession number format (10-2-6 digits)."""
    s = val.strip()
    if not ACCESSION_PATTERN.match(s):
        raise ValueError(f"Invalid accession number format: {val}")
    return AccessionNo(s)


def parse_ticker(val: str) -> Ticker:
    """Validate uppercase exchange ticker symbol."""
    s = val.strip().upper()
    if not TICKER_PATTERN.match(s):
        raise ValueError(f"Invalid ticker format: {val}")
    return Ticker(s)


def parse_usd(val: str | Decimal | int) -> UsdPerShare:
    """Validate and construct USD price per share using Decimal."""
    if isinstance(val, float):
        raise TypeError("Float values are strictly forbidden for money fields.")
    try:
        d = Decimal(str(val).replace("$", "").replace(",", "").strip())
    except (InvalidOperation, ValueError) as err:
        raise ValueError(f"Invalid USD price per share: {val}") from err
    if d <= Decimal("0"):
        raise ValueError(f"Offer price must be positive: {val}")
    return UsdPerShare(d)


def parse_share_count(val: str | int) -> ShareCount:
    """Validate and construct integer positive share count."""
    if isinstance(val, float):
        raise TypeError("Float values are forbidden for share counts.")
    try:
        if isinstance(val, str):
            clean = val.replace(",", "").strip()
            count = int(clean)
        else:
            count = int(val)
    except ValueError as err:
        raise ValueError(f"Invalid share count: {val}") from err
    if count <= 0:
        raise ValueError(f"Share count must be positive integer: {val}")
    return ShareCount(count)


def parse_usd_amount(val: str | Decimal | int) -> UsdAmount:
    """Validate and construct USD amount using Decimal."""
    if isinstance(val, float):
        raise TypeError("Float values are strictly forbidden for money amounts.")
    try:
        d = Decimal(str(val).replace("$", "").replace(",", "").strip())
    except (InvalidOperation, ValueError) as err:
        raise ValueError(f"Invalid USD amount: {val}") from err
    if d < Decimal("0"):
        raise ValueError(f"Amount must not be negative: {val}")
    return UsdAmount(d)
