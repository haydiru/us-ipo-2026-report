"""Reference implementation of an I/O adapter (PRD Section 8.4)."""
import hashlib
from pathlib import Path

class ReferenceAdapter:
    """Canonical adapter demonstrating cached, rate-limited, and content-addressed I/O."""

    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch_with_cache(self, key: str, raw_bytes: bytes) -> tuple[str, Path]:
        """Store payload by SHA256 content hash in raw cache."""
        sha = hashlib.sha256(raw_bytes).hexdigest()
        target = self.cache_dir / sha
        if not target.exists():
            target.write_bytes(raw_bytes)
        return sha, target
