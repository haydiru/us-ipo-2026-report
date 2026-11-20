"""Unit tests for Stage S0: Run Initialization."""

from datetime import UTC, date, datetime
from pathlib import Path

import pytest
import yaml

from ipo_ledger.clock import FrozenClock
from ipo_ledger.pipeline.init_run import StageS0Init


def test_s0_init_success(tmp_path: Path) -> None:
    """Verify S0 creates manifest and sqlite entry with frozen parameters."""
    cfg_data = {
        "version": "1.0",
        "as_of_date": "2026-11-20",
        "window_start": "2026-01-01",
        "window_end": "2026-11-20",
        "exchanges": {"included": ["NASDAQ", "NYSE"], "excluded": ["OTC"]},
        "offerings": {"direct_listings": False, "spac_mergers": False},
        "rate_limits": {"sec_user_agent": "TestAgent test@example.com"},
    }
    cfg_file = tmp_path / "rules.yaml"
    cfg_file.write_text(yaml.dump(cfg_data), encoding="utf-8")

    runs_dir = tmp_path / "runs"
    clock = FrozenClock(datetime(2026, 11, 20, 12, 0, 0, tzinfo=UTC))
    s0 = StageS0Init(clock=clock, runs_dir=runs_dir)

    manifest = s0.run(config_path=cfg_file, run_id="run_test_01")
    assert manifest.status == "ready"
    assert manifest.as_of_date == date(2026, 11, 20)
    assert (runs_dir / "run_test_01" / "manifest.json").exists()
    assert (runs_dir / "run_test_01" / "ledger.sqlite").exists()


def test_s0_init_invalid_window(tmp_path: Path) -> None:
    """Verify S0 rejects invalid window ranges."""
    cfg_data = {
        "version": "1.0",
        "as_of_date": "2026-11-20",
        "window_start": "2026-12-01",
        "window_end": "2026-11-20",
        "exchanges": {"included": ["NASDAQ"]},
        "offerings": {},
    }
    cfg_file = tmp_path / "invalid_rules.yaml"
    cfg_file.write_text(yaml.dump(cfg_data), encoding="utf-8")

    runs_dir = tmp_path / "runs"
    clock = FrozenClock(datetime(2026, 11, 20, 12, 0, 0, tzinfo=UTC))
    s0 = StageS0Init(clock=clock, runs_dir=runs_dir)

    with pytest.raises(ValueError, match="window_start must be <= window_end"):
        s0.run(config_path=cfg_file)
