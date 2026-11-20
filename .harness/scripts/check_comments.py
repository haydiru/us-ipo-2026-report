"""Comment policy checker enforcing PRD Section 8.3."""
import io
import re
import sys
import tokenize
from pathlib import Path

TODO_PATTERN = re.compile(r"^#\s*TODO\([A-Za-z0-9_-]+\):")
IGNORE_PATTERN = re.compile(r"^#\s*(noqa|type:\s*ignore)")

def check_file(path: Path) -> list[str]:
    errors = []
    with open(path, "rb") as f:
        content = f.read()
    
    tokens = tokenize.tokenize(io.BytesIO(content).readline)
    for tok in tokens:
        if tok.type == tokenize.COMMENT:
            text = tok.string.strip()
            # Allowed comments:
            # 1. shebang or encoding or pragma
            if text.startswith("#!") or text.startswith("# -*-"):
                continue
            # 2. type ignores or noqa
            if IGNORE_PATTERN.match(text):
                continue
            # 3. TODO with ticket format
            if TODO_PATTERN.match(text):
                continue
            # 4. Standard license / copyright or contract header
            if text.startswith("# Copyright") or text.startswith("# License") or text.startswith("# Contract:"):
                continue
            errors.append(f"{path}:{tok.start[0]}: IPO009 Comment '{text}' is not permitted by comment policy.")
    return errors

def main() -> int:
    root = Path(__file__).resolve().parent.parent.parent
    src_dir = root / "src"
    all_errors = []
    if src_dir.exists():
        for py_file in src_dir.rglob("*.py"):
            all_errors.extend(check_file(py_file))
    
    if all_errors:
        for err in all_errors:
            print(err, file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
