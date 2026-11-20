"""Stage S0: Run Initialization and Configuration (PRD Section 3.1)."""

import hashlib
from datetime import date
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from ipo_ledger.adapters.storage import LedgerStorage
from ipo_ledger.clock import Clock
from ipo_ledger.domain.schema import RunManifestModel


class ConfigSchema(BaseModel):
    """Schema for universe rules configuration."""

    version: str
    as_of_date: date
    window_start: date
    window_end: date
    exchanges: dict[str, list[str]]
    offerings: dict[str, object]
    rate_limits: dict[str, object] = Field(default_factory=dict)


class StageS0Init:
    """Stage S0 orchestrator freezing parameters into manifest.json."""

    def __init__(self, clock: Clock, runs_dir: Path) -> None:
        self.clock = clock
        self.runs_dir = runs_dir

    def run(self, config_path: Path, run_id: str | None = None) -> RunManifestModel:
        """Validate config, freeze manifest, and persist run entity."""
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        raw_bytes = config_path.read_bytes()
        rule_hash = hashlib.sha256(raw_bytes).hexdigest()
        data = yaml.safe_load(raw_bytes)
        cfg = ConfigSchema(**data)

        if cfg.window_start > cfg.window_end:
            raise ValueError("window_start must be <= window_end")
        if cfg.window_end != cfg.as_of_date:
            raise ValueError("window_end must equal as_of_date")

        now_str = self.clock.now().strftime("%Y%m%d_%H%M%S")
        active_run_id = run_id or f"run_{now_str}"
        run_folder = self.runs_dir / active_run_id
        run_folder.mkdir(parents=True, exist_ok=True)

        user_agent = str(
            cfg.rate_limits.get(
                "sec_user_agent",
                "IPOLedgerAgent research@ipoledger.internal",
            )
        )

        manifest = RunManifestModel(
            run_id=active_run_id,
            as_of_date=cfg.as_of_date,
            rule_hash=rule_hash,
            tool_versions={
                "python": "3.13",
                "pydantic": "2.13.4",
                "xlsxwriter": "3.3.3",
            },
            edgar_user_agent=user_agent,
            status="ready",
            created_at=self.clock.now().isoformat(),
        )

        manifest_file = run_folder / "manifest.json"
        manifest_file.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")

        db_file = run_folder / "ledger.sqlite"
        storage = LedgerStorage(db_file)
        storage.save_run(manifest)

        return manifest
