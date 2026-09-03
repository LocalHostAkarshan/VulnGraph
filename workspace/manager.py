from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


BASE_WORKSPACE = Path("workspaces")


@dataclass(frozen=True)
class Workspace:
    root: Path
    repository: Path
    metadata: Path
    artifacts: Path
    logs: Path
    results: Path


def create_workspace(job_id: str) -> Workspace:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", job_id):
        raise ValueError("Invalid job_id.")

    root = (BASE_WORKSPACE / job_id).resolve()

    if root.exists():
        raise FileExistsError(f"Workspace already exists: {root}")

    repository = root / "repository"
    metadata = root / "metadata"
    artifacts = root / "artifacts"
    logs = root / "logs"
    results = root / "results"

    for path in (
        repository,
        metadata,
        artifacts,
        logs,
        results,
    ):
        path.mkdir(parents=True, exist_ok=False)

    return Workspace(
        root=root,
        repository=repository,
        metadata=metadata,
        artifacts=artifacts,
        logs=logs,
        results=results,
    )
