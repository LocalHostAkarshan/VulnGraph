from __future__ import annotations

from .schema import REPOSITORY_MANIFEST_SCHEMA


def build_repository_manifest(
    metadata,
    job_id: str,
    clone_result: dict,
    source_inventory: dict,
    manifests: list[dict],
    project: dict,
    languages: list[dict],
    frameworks: list[dict],
) -> dict:
    source_bytes = sum(
        item["size_bytes"]
        for item in source_inventory["files"]
    )

    return {
        "schema_version": "1.0",
        "repository": {
            "owner": metadata.name_with_owner.split("/", 1)[0],
            "name": metadata.name,
            "full_name": metadata.name_with_owner,
            "url": metadata.url,
            "visibility": "private" if metadata.is_private else "public",
            "default_branch": metadata.default_branch,
            "commit_sha": metadata.commit_sha,
            "is_fork": metadata.is_fork,
            "is_archived": metadata.is_archived,
        },
        "ingestion": {
            "job_id": job_id,
            "method": "github_graphql+git",
            "clone_type": "shallow",
            "clone_depth": clone_result["clone_depth"],
            "history_downloaded": clone_result["history_downloaded"],
            "size_limit_bytes": 500 * 1024 * 1024,
            "status": "completed",
        },
        "statistics": {
            "repository_size_bytes": clone_result["size_bytes"],
            "source_file_count": source_inventory["file_count"],
            "source_bytes": source_bytes,
            "manifest_file_count": len(manifests),
        },
        "languages": languages,
        "project": project,
        "frameworks": frameworks,
        "manifests": [
            {
                **manifest,
                "status": "discovered",
            }
            for manifest in manifests
        ],
        "analysis_ready": True,
        "_schema": REPOSITORY_MANIFEST_SCHEMA,
    }
