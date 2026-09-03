from __future__ import annotations

from typing import Any


REPOSITORY_MANIFEST_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Repo Auditor Repository Manifest",
    "type": "object",
    "required": [
        "schema_version",
        "repository",
        "ingestion",
        "statistics",
        "languages",
        "project",
        "frameworks",
        "manifests",
        "analysis_ready",
    ],
    "properties": {
        "schema_version": {"type": "string"},
        "repository": {"type": "object"},
        "ingestion": {"type": "object"},
        "statistics": {"type": "object"},
        "languages": {"type": "array"},
        "project": {"type": "object"},
        "frameworks": {"type": "array"},
        "manifests": {"type": "array"},
        "analysis_ready": {"type": "boolean"},
    },
}
