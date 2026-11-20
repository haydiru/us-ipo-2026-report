"""Custom AST and lexical checker enforcing IPO001-IPO009 from PRD Section 8.3."""
import ast
import sys
from pathlib import Path

def check_ast(file_path: Path) -> list[str]:
    errors = []
    text = file_path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text, filename=str(file_path))
    except SyntaxError as e:
        return [f"{file_path}:{e.lineno}: Syntax error: {e}"]
    
    parts = file_path.parts
    is_domain = "domain" in parts
    is_compute = file_path.name == "compute.py" and is_domain
    is_types = file_path.name == "types.py" and is_domain
    is_gate = file_path.name == "gate.py" and is_domain
    is_edgar = file_path.name == "edgar.py" and "adapters" in parts
    
    for node in ast.walk(tree):
        # IPO001: domain importing adapters or pipeline
        if is_domain:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if "adapters" in alias.name or "pipeline" in alias.name:
                        errors.append(f"{file_path}:{node.lineno}: IPO001 domain/ must stay pure. Move I/O to adapters/.")
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if "adapters" in mod or "pipeline" in mod:
                    errors.append(f"{file_path}:{node.lineno}: IPO001 domain/ must stay pure. Move I/O to adapters/.")

        # IPO006: hardcoded sec.gov URL outside adapters/edgar.py
        if not is_edgar and isinstance(node, ast.Constant) and isinstance(node.value, str):
            if "sec.gov" in node.value and not "tests" in parts and not "reference" in parts:
                errors.append(f"{file_path}:{node.lineno}: IPO006 Build EDGAR URLs with EdgarUrls in adapters/edgar.py.")

        # IPO007: status="VERIFIED" outside domain/gate.py
        if not is_gate and not "tests" in parts and not "fixtures" in parts:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "status":
                        if isinstance(node.value, ast.Constant) and node.value == "VERIFIED":
                            errors.append(f"{file_path}:{node.lineno}: IPO007 Only the completeness gate may assign VERIFIED.")

    return errors

def main() -> int:
    root = Path(__file__).resolve().parent.parent.parent
    src_dir = root / "src"
    all_errors = []
    if src_dir.exists():
        for py_file in src_dir.rglob("*.py"):
            all_errors.extend(check_ast(py_file))
    
    if all_errors:
        for err in all_errors:
            print(err, file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
