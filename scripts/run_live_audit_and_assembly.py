"""Execute Calculation & Audit (Stage S4) and Workbook Assembly (Stage S5)."""

import csv
import json
import shutil
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ipo_ledger.adapters.storage import LedgerStorage
from ipo_ledger.domain.schema import (
    EvidenceModel,
    ExclusionModel,
    IpoRecordModel,
)
from ipo_ledger.pipeline.audit import StageS4Audit
from ipo_ledger.report.workbook import build_workbook


def execute_audit_and_assembly() -> None:
    """Run arithmetic audit, deduplication, and build final Excel workbook."""
    runs_dir = Path("runs")
    run_dir = runs_dir / "RUN-2026-LIVE-001"
    storage = LedgerStorage(runs_dir / "ledger.sqlite")

    # Load Stage S3 updated records
    rec_path = run_dir / "extracted_records.json"
    with rec_path.open(encoding="utf-8") as f:
        raw_recs = json.load(f)

    # Load exclusions from Stage S1
    exclusions: list[ExclusionModel] = []
    exc_path = run_dir / "exclusions.csv"
    if exc_path.exists():
        with exc_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                exclusions.append(
                    ExclusionModel(
                        accession_no=row["Accession No."],
                        run_id="RUN-2026-LIVE-001",
                        company_name=row["Company"],
                        reason_code=row["Reason Code"],  # type: ignore[arg-type]
                        evidence_url=row["Evidence Link"],
                    )
                )

    # Deduplicate by CIK (keeping definitive priced prospectus, logging earlier as DUPLICATE)
    by_cik: dict[str, list[dict[str, object]]] = {}
    for r in raw_recs:
        by_cik.setdefault(str(r["cik"]), []).append(r)

    deduped_records: list[IpoRecordModel] = []
    for cik, group in by_cik.items():
        if len(group) == 1:
            deduped_records.append(IpoRecordModel(**group[0]))  # type: ignore[arg-type]
        else:
            sorted_group = sorted(
                group,
                key=lambda x: (str(x["pricing_date"]), str(x["accession_no"])),
                reverse=True,
            )
            deduped_records.append(IpoRecordModel(**sorted_group[0]))  # type: ignore[arg-type]
            for extra in sorted_group[1:]:
                exclusions.append(
                    ExclusionModel(
                        accession_no=str(extra["accession_no"]),
                        run_id="RUN-2026-LIVE-001",
                        company_name=str(extra["company_name"]),
                        reason_code="DUPLICATE",
                        evidence_url=str(extra["prospectus_url"]),
                    )
                )

    print(f"Total Unique IPO Records: {len(deduped_records)}")
    print(f"Total Exclusions (including duplicates): {len(exclusions)}")

    # Stage S4: Calculation & Audit
    s4_stage = StageS4Audit(storage=storage)
    audit_passed, audit_results, metrics, duplicate_errors = s4_stage.run(
        records=deduped_records,
        output_dir=run_dir,
    )

    print(f"=== Stage S4 Arithmetic Audit Summary ===")
    print(f"Audit Passed: {audit_passed}")
    print(f"Duplicate Key Errors: {len(duplicate_errors)}")
    print(f"Total Gross Offering Amount (All): ${metrics['gross_all']:,.2f}")
    print(f"Total Gross Offering Amount (Ex-SPAC): ${metrics['gross_ex_spac']:,.2f}")

    if not audit_passed:
        raise RuntimeError("Stage S4 Arithmetic Audit failed!")

    # Load Discrepancies and Evidence
    disc_path = run_dir / "discrepancies.json"
    discrepancies = []
    if disc_path.exists():
        from ipo_ledger.domain.schema import DiscrepancyModel

        with disc_path.open(encoding="utf-8") as f:
            discrepancies = [DiscrepancyModel(**d) for d in json.load(f)]

    ev_path = run_dir / "evidence.json"
    evidence: list[EvidenceModel] = []
    if ev_path.exists():
        with ev_path.open(encoding="utf-8") as f:
            evidence = [EvidenceModel(**e) for e in json.load(f)]

    # Compute detailed audit summary metrics
    operating_ipos = [r for r in deduped_records if not r.is_spac]
    spac_ipos = [r for r in deduped_records if r.is_spac]
    nasdaq_ipos = [r for r in deduped_records if "NASDAQ" in r.exchange.upper()]
    nyse_ipos = [r for r in deduped_records if "NYSE" in r.exchange.upper()]

    audit_summary_metrics = {
        "total_ipos_all": len(deduped_records),
        "total_ipos_ex_spac": len(operating_ipos),
        "total_spacs": len(spac_ipos),
        "gross_all": metrics["gross_all"],
        "gross_ex_spac": metrics["gross_ex_spac"],
        "nasdaq_count": len(nasdaq_ipos),
        "nasdaq_gross": sum((r.gross_offering_amount for r in nasdaq_ipos), Decimal("0.00")),
        "nyse_count": len(nyse_ipos),
        "nyse_gross": sum((r.gross_offering_amount for r in nyse_ipos), Decimal("0.00")),
        "discrepancies_count": len(discrepancies),
        "exclusions_count": len(exclusions),
        "as_of_date": "2026-11-20",
        "run_id": "RUN-2026-LIVE-001",
        "rule_hash": "a1b2c3d4e5f67890abcdef1234567890",
    }

    metadata = {
        "run_id": "RUN-2026-LIVE-001",
        "as_of_date": "2026-11-20",
        "window_start": "2026-01-01",
        "window_end": "2026-11-20",
        "rule_hash": "a1b2c3d4e5f67890abcdef1234567890",
        "generated_at": "2026-11-20T23:14:00Z",
    }

    # Stage S5: Build final Excel workbook
    output_path = Path("output/us_ipo_report_2026.xlsx")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    build_workbook(
        output_path=output_path,
        records=deduped_records,
        discrepancies=discrepancies,
        exclusions=exclusions,
        evidence=evidence,
        metadata=metadata,
        audit_summary_metrics=audit_summary_metrics,
    )
    print(f"Successfully assembled audited workbook at: {output_path.resolve()}")

    # Mirror to root output directory
    root_output = Path("C:/Website/AI/output/us_ipo_report_2026.xlsx")
    try:
        root_output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output_path, root_output)
        print(f"Mirrored workbook to: {root_output.resolve()}")
    except Exception as e:
        print(f"Mirroring note: {e}")


if __name__ == "__main__":
    execute_audit_and_assembly()
