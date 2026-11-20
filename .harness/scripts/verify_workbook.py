"""Runtime workbook verification script using openpyxl."""
import sys
from decimal import Decimal
from pathlib import Path
import openpyxl

EXPECTED_SHEETS = [
    "IPO_Report",
    "Audit_Summary",
    "Discrepancy_Log",
    "Exclusions",
    "Source_Evidence",
    "Run_Metadata"
]

EXPECTED_W1_HEADERS = [
    "Company",
    "Ticker",
    "Exchange",
    "Pricing Date",
    "Offer Price",
    "Base Shares Offered",
    "Gross Offering Amount",
    "SEC Final Prospectus",
    "Form Type",
    "Accession No.",
    "Security Type",
    "Is_SPAC",
    "Status",
    "Flag Codes"
]

def verify_workbook(path: Path) -> list[str]:
    errors = []
    if not path.exists():
        return [f"Workbook file does not exist: {path}"]
    
    wb = openpyxl.load_workbook(path, data_only=False)
    sheet_names = wb.sheetnames
    for s in EXPECTED_SHEETS:
        if s not in sheet_names:
            errors.append(f"Missing expected sheet: {s}")
    
    if "IPO_Report" in sheet_names:
        ws = wb["IPO_Report"]
        # Check headers
        headers = [ws.cell(row=1, column=col).value for col in range(1, len(EXPECTED_W1_HEADERS) + 1)]
        if headers != EXPECTED_W1_HEADERS:
            errors.append(f"Header mismatch in IPO_Report. Found: {headers}, Expected: {EXPECTED_W1_HEADERS}")
        
        # Check rows
        prev_date = None
        prev_ticker = ""
        row_idx = 2
        while ws.cell(row=row_idx, column=1).value is not None:
            comp = ws.cell(row=row_idx, column=1).value
            ticker = str(ws.cell(row=row_idx, column=2).value or "")
            pricing_date = ws.cell(row=row_idx, column=4).value
            price = ws.cell(row=row_idx, column=5).value
            shares = ws.cell(row=row_idx, column=6).value
            formula = str(ws.cell(row=row_idx, column=7).value or "")
            link = ws.cell(row=row_idx, column=8).hyperlink

            # Check chronological sort: pricing_date ascending, ticker ascending
            date_str = str(pricing_date)
            if prev_date is not None:
                if date_str < prev_date:
                    errors.append(f"Row {row_idx}: Date {date_str} is out of chronological order (prev {prev_date})")
                elif date_str == prev_date and ticker < prev_ticker:
                    errors.append(f"Row {row_idx}: Ticker {ticker} is out of alphabetical order for date {date_str}")
            prev_date = date_str
            prev_ticker = ticker

            # Check formula
            expected_formula = f"=E{row_idx}*F{row_idx}"
            alt_formula = f"=F{row_idx}*E{row_idx}"
            if not (formula.startswith("=") and ("E" in formula and "F" in formula)):
                errors.append(f"Row {row_idx}: Gross Offering Amount formula is invalid: {formula}")

            # Check hyperlink
            if link and link.target:
                if "sec.gov" not in link.target:
                    errors.append(f"Row {row_idx}: Hyperlink target does not point to sec.gov: {link.target}")

            row_idx += 1

    wb.close()
    return errors

def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python verify_workbook.py <path_to_xlsx>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    errors = verify_workbook(path)
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1
    print(f"SUCCESS: Workbook {path} passed verification.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
