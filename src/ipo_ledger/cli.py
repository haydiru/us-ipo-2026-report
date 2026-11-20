"""CLI entry point for the US IPO Ledger pipeline (PRD Section 4.1)."""

import argparse
import sys
from pathlib import Path

from ipo_ledger.clock import SystemClock
from ipo_ledger.pipeline.init_run import StageS0Init


def main() -> int:
    """Parse arguments and dispatch to pipeline stages."""
    parser = argparse.ArgumentParser(description="US IPO Ledger 2026 CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_p = subparsers.add_parser("init", help="Initialize run and freeze parameters")
    init_p.add_argument("--as-of", default="2026-11-20", help="Reference as-of date (YYYY-MM-DD)")
    init_p.add_argument(
        "--config", default="config/universe_rules.yaml", help="Path to universe rules"
    )

    subparsers.add_parser("discover", help="Stage S1: Discover universe from EDGAR & calendars")
    subparsers.add_parser("extract", help="Stage S2: Extract terms from final prospectuses")
    subparsers.add_parser("crosscheck", help="Stage S3: Multi-source verification")
    subparsers.add_parser("audit", help="Stage S4: Dual-method arithmetic audit")
    subparsers.add_parser("build", help="Stage S5: Build 6-sheet Excel workbook")
    subparsers.add_parser("gate", help="Stage S6: Evaluate completeness gate")

    args = parser.parse_args()

    if args.command == "init":
        clock = SystemClock()
        s0 = StageS0Init(clock=clock, runs_dir=Path("runs"))
        manifest = s0.run(config_path=Path(args.config))
        sys.stdout.write(f"Run initialized: {manifest.run_id}\n")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
