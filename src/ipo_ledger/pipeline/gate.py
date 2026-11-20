"""Stage S6: Completeness Gate pipeline orchestrator (PRD Section 3.8)."""

import json
from pathlib import Path

from ipo_ledger.adapters.edgar import EdgarUrls
from ipo_ledger.adapters.storage import LedgerStorage
from ipo_ledger.domain.gate import evaluate_gate
from ipo_ledger.domain.schema import GateResultModel, IpoRecordModel


class StageS6Gate:
    """Stage S6 orchestrator evaluating completeness conditions."""

    def __init__(self, storage: LedgerStorage) -> None:
        self.storage = storage

    def run(
        self,
        run_id: str,
        records: list[IpoRecordModel],
        unmatched_calendar_rows: list[dict[str, str]],
        manual_queue_count: int,
        calc_audit_passed: bool,
        duplicate_count: int,
        output_dir: Path,
    ) -> GateResultModel:
        """Evaluate completeness gate and save verdict."""
        output_dir.mkdir(parents=True, exist_ok=True)

        universe_reconciled = len(unmatched_calendar_rows) == 0
        manual_queue_empty = manual_queue_count == 0
        no_duplicates = duplicate_count == 0

        urls_valid = all(r.prospectus_url.startswith(EdgarUrls.BASE_URL) for r in records)
        crosscheck_complete = all(
            r.status == "VERIFIED"
            or "SINGLE_SOURCE" in r.flag_codes
            or "DISCREPANCY_RESOLVED" in r.flag_codes
            for r in records
        )

        gate_result = evaluate_gate(
            run_id=run_id,
            universe_reconciled=universe_reconciled,
            urls_valid=urls_valid,
            manual_queue_empty=manual_queue_empty,
            calc_audit_passed=calc_audit_passed,
            no_duplicates=no_duplicates,
            crosscheck_complete=crosscheck_complete,
        )

        self.storage.save_gate_result(gate_result)

        gate_path = output_dir / "gate_result.json"
        gate_path.write_text(
            json.dumps(gate_result.model_dump(mode="json"), indent=2),
            encoding="utf-8",
        )

        return gate_result
