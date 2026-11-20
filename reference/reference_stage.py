"""Reference implementation of a pipeline stage (PRD Section 8.4)."""
from pathlib import Path
from typing import Any
from ipo_ledger.clock import Clock

class ReferenceStage:
    """Canonical stage illustrating typed input, pure domain execution, and typed output."""

    def __init__(self, clock: Clock) -> None:
        self.clock = clock

    def run(self, input_path: Path, output_path: Path) -> dict[str, Any]:
        """Execute the stage deterministically with isolated file boundaries."""
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        execution_time = self.clock.now().isoformat()
        result = {
            "status": "completed",
            "executed_at": execution_time,
            "records_processed": 0,
        }
        output_path.write_text("{}", encoding="utf-8")
        return result
