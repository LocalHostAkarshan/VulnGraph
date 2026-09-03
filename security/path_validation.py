from __future__ import annotations

from pathlib import Path


class UnsafePathError(ValueError):
    pass


def safe_join(root: Path, relative_path: str) -> Path:
    root = root.resolve()
    candidate = (root / relative_path).resolve()

    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise UnsafePathError(
            f"Path escapes workspace: {relative_path}"
        ) from exc

    return candidate
