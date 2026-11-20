"""Content-addressed raw file cache (PRD Section 2.3, 5.1)."""

import hashlib
from pathlib import Path


class ContentCache:
    """Store and retrieve raw HTTP payloads by content hash."""

    def __init__(self, base_dir: Path) -> None:
        self.raw_dir = base_dir / "raw"
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def put(self, data: bytes) -> tuple[str, Path]:
        """Store bytes by SHA256 content hash and return hash and path."""
        sha = hashlib.sha256(data).hexdigest()
        target = self.raw_dir / sha
        if not target.exists():
            target.write_bytes(data)
        return sha, target

    def get(self, sha: str) -> bytes | None:
        """Retrieve cached bytes by SHA256 hash if present."""
        target = self.raw_dir / sha
        if target.exists():
            return target.read_bytes()
        return None

    def has(self, sha: str) -> bool:
        """Check if content hash exists in cache."""
        return (self.raw_dir / sha).exists()
