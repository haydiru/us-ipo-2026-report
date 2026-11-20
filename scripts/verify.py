"""Verification runner executing the pre-merge gate pipeline (PRD Section 8.5)."""
import os
import subprocess
import sys
from pathlib import Path

def run_step(name: str, cmd: list[str], cwd: Path) -> bool:
    print(f"\n==================== [GATE STEP] {name} ====================")
    env = os.environ.copy()
    src_path = str(cwd / "src")
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{src_path}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = src_path
    res = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, env=env)
    if res.stdout:
        print(res.stdout)
    if res.stderr:
        print(res.stderr, file=sys.stderr)
    if res.returncode != 0:
        print(f"FAILED: {name} exited with code {res.returncode}")
        return False
    print(f"PASSED: {name}")
    return True

def main() -> int:
    root = Path(__file__).resolve().parent.parent
    steps = [
        ("Linting (Ruff)", [sys.executable, "-m", "ruff", "check", "src", "tests"]),
        ("Comment Policy", [sys.executable, ".harness/scripts/check_comments.py"]),
        ("Custom Rules (IPO0xx)", [sys.executable, ".harness/scripts/lint_custom.py"]),
        ("Typecheck (Mypy Strict)", [sys.executable, "-m", "mypy", "--strict", "src", "tests"]),
        ("Unit Tests (Pytest)", [sys.executable, "-m", "pytest", "tests/unit", "-v"]),
    ]

    for name, cmd in steps:
        if not run_step(name, cmd, root):
            return 1

    print("\n==================== ALL PRE-MERGE GATES PASSED ====================")
    return 0

if __name__ == "__main__":
    sys.exit(main())
