"""Injectable Clock protocol for deterministic run timestamps."""

from datetime import UTC, date, datetime
from typing import Protocol


class Clock(Protocol):
    """Protocol for time providers."""

    def now(self) -> datetime:
        """Return current datetime in UTC."""
        ...

    def today(self) -> date:
        """Return current date in UTC."""
        ...


class SystemClock:
    """Production clock using system time in UTC."""

    def now(self) -> datetime:
        return datetime.now(UTC)

    def today(self) -> date:
        return datetime.now(UTC).date()


class FrozenClock:
    """Deterministic frozen clock for testing and reproducible runs."""

    def __init__(self, frozen_dt: datetime) -> None:
        self._dt = frozen_dt

    def now(self) -> datetime:
        return self._dt

    def today(self) -> date:
        return self._dt.date()
