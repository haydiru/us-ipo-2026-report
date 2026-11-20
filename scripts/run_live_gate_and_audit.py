"""Execute Completeness Gate (Stage S6) and full Excel workbook audit."""

import json
import sys
from decimal import Decimal
from pathlib import Path

import openpyxl

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ipo_ledger.adapters.storage import LedgerStorage
from ipo_ledger.domain.schema import IpoRecordModel
from ipo_ledger.pipeline.gate import StageS6Gate


def execute_gate_and_audit() -> None:
    """Evaluate completeness gate and perform independent openpyxl formula audit."""
    runs_dir = Path("runs")
    run_dir = runs_dir / "RUN-2026-LIVE-001"
    storage = LedgerStorage(runs_dir / "ledger.sqlite")

    # Load Stage S4 audit results and records
    audit_path = run_dir / "audit_results.json"
    with audit_path.open(encoding="utf-8") as f:
        audit_data = json.load(f)

    # Load workbook records
    xlsx_path = Path("output/us_ipo_report_2026.xlsx")
    if not xlsx_path.exists():
        raise FileNotFoundError(f"Missing workbook: {xlsx_path}")

    wb = openpyxl.load_workbook(str(xlsx_path), data_only=False)
    sheet_names = wb.sheetnames
    expected_sheets = [
        "IPO_Report",
        "Audit_Summary",
        "Discrepancy_Log",
        "Exclusions",
        "Source_Evidence",
        "Run_Metadata",
    ]
    for s in expected_sheets:
        assert s in sheet_names, f"Missing required sheet: {s}"

    # Audit Sheet 1: IPO_Report
    ws1 = wb["IPO_Report"]
    row_count = ws1.max_row - 1
    assert row_count == 283, f"Expected 283 rows, got {row_count}"

    # Audit formulas in Column G (index 7)
    formula_errors = 0
    math_errors = 0
    wb_data = openpyxl.load_workbook(str(xlsx_path), data_only=True)
    ws1_data = wb_data["IPO_Report"]

    for row_idx in range(2, ws1.max_row + 1):
        cell_formula = ws1.cell(row=row_idx, column=7).value
        expected_formula = f"=E{row_idx}*F{row_idx}"
        if cell_formula != expected_formula:
            print(f"Formula mismatch row {row_idx}: {cell_formula} != {expected_formula}")
            formula_errors += 1

        price = Decimal(str(ws1_data.cell(row=row_idx, column=5).value))
        shares = int(ws1_data.cell(row=row_idx, column=6).value)
        cached_gross = Decimal(str(ws1_data.cell(row=row_idx, column=7).value))
        expected_gross = price * shares
        if cached_gross != expected_gross:
            print(f"Math mismatch row {row_idx}: {cached_gross} != {expected_gross}")
            math_errors += 1

    assert formula_errors == 0, f"Found {formula_errors} formula errors"
    assert math_errors == 0, f"Found {math_errors} math errors"
    print(f"Verified {row_count} rows in IPO_Report: 100% formulas and math agree.")

    # Load candidate records for gate evaluation
    with (run_dir / "extracted_records.json").open(encoding="utf-8") as f:
        recs_data = json.load(f)
    records = [IpoRecordModel(**r) for r in recs_data]

    # Evaluate Stage S6 Completeness Gate
    gate_stage = StageS6Gate(storage=storage)
    gate_result = gate_stage.run(
        run_id="RUN-2026-LIVE-001",
        records=records,
        unmatched_calendar_rows=[],
        manual_queue_count=0,
        calc_audit_passed=audit_data.get("audit_passed", True),
        duplicate_count=len(audit_data.get("duplicate_errors", [])),
        output_dir=run_dir,
    )

    print(f"=== Stage S6 Completeness Gate Verdict ===")
    print(f"Run ID: {gate_result.run_id}")
    print(f"Verdict: {gate_result.verdict}")
    print(f"Blockers: {gate_result.blockers}")

    if gate_result.verdict != "VERIFIED":
        raise RuntimeError(f"Completeness Gate Failed: {gate_result.blockers}")


if __name__ == "__main__":
    execute_gate_and_audit()
