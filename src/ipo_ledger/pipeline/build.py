"""Stage S5: Workbook Assembly orchestration (PRD Section 3.6)."""

from pathlib import Path
from typing import Any

from ipo_ledger.domain.schema import (
    DiscrepancyModel,
    EvidenceModel,
    ExclusionModel,
    IpoRecordModel,
)
from ipo_ledger.report.workbook import build_workbook


class StageS5Build:
    """Stage S5 orchestrator building the final auditable Excel deliverable."""

    def run(
        self,
        output_xlsx_path: Path,
        records: list[IpoRecordModel],
        discrepancies: list[DiscrepancyModel],
        exclusions: list[ExclusionModel],
        evidence: list[EvidenceModel],
        metadata: dict[str, str],
        audit_summary_metrics: dict[str, Any],
    ) -> Path:
        """Assemble all 6 sheets into .xlsx."""
        build_workbook(
            output_path=output_xlsx_path,
            records=records,
            discrepancies=discrepancies,
            exclusions=exclusions,
            evidence=evidence,
            metadata=metadata,
            audit_summary_metrics=audit_summary_metrics,
        )
        return output_xlsx_path
