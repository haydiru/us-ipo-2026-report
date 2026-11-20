"""Stage S4: Computation and Independent Recompute Audit (PRD Section 3.5)."""

import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from ipo_ledger.adapters.storage import LedgerStorage
from ipo_ledger.domain.compute import (
    audit_dataset_math,
    check_duplicates,
)
from ipo_ledger.domain.schema import AuditResultModel, IpoRecordModel


class StageS4Audit:
    """Stage S4 orchestrator verifying dual-method arithmetic and deduplication."""

    def __init__(self, storage: LedgerStorage) -> None:
        self.storage = storage

    def run(
        self,
        records: list[IpoRecordModel],
        output_dir: Path,
    ) -> tuple[bool, list[AuditResultModel], dict[str, Any], list[str]]:
        """Run arithmetic audit, duplicate checks, and persist results."""
        output_dir.mkdir(parents=True, exist_ok=True)

        duplicate_errors = check_duplicates(records)
        results, totals = audit_dataset_math(records)

        self.storage.save_audit_results(results)

        audit_passed = totals.passed and (len(duplicate_errors) == 0)

        metrics = {
            "total_ipos_all": len(records),
            "total_ipos_ex_spac": len([r for r in records if not r.is_spac]),
            "gross_all": totals.total_gross_decimal,
            "gross_ex_spac": sum(
                (r.gross_offering_amount for r in records if not r.is_spac),
                Decimal("0.00"),
            ),
            "audit_passed": audit_passed,
            "duplicate_count": len(duplicate_errors),
        }

        audit_path = output_dir / "audit_results.json"
        audit_path.write_text(
            json.dumps(
                {
                    "audit_passed": audit_passed,
                    "totals": {
                        "total_records": totals.total_records,
                        "total_gross_decimal": str(totals.total_gross_decimal),
                        "total_gross_recompute": str(totals.total_gross_recompute),
                    },
                    "duplicate_errors": duplicate_errors,
                    "records_audited": [r.model_dump(mode="json") for r in results],
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        return audit_passed, results, metrics, duplicate_errors
