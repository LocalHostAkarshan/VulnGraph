from __future__ import annotations

from pathlib import Path

from .github_auth import get_installation_token
from .github_graphql import fetch_repository_metadata
from .repository_validator import validate_repository
from .shallow_clone import shallow_clone

from repo_auditor.discovery.source_detector import scan_source_files
from repo_auditor.discovery.manifest_detector import find_manifests
from repo_auditor.discovery.project_detector import detect_project
from repo_auditor.discovery.language_detector import detect_languages
from repo_auditor.discovery.framework_detector import detect_frameworks
from repo_auditor.manifests.builder import build_repository_manifest
from repo_auditor.manifests.serializers import write_json
from repo_auditor.workspace.manager import create_workspace


def run_repository_ingestion(repo_url: str, job_id: str) -> dict:
    owner, repo = _parse_github_url(repo_url)

    workspace = create_workspace(job_id)

    installation = get_installation_token()

    metadata = fetch_repository_metadata(
        token=installation.token,
        owner=owner,
        repo=repo,
    )

    validate_repository(metadata)

    clone_result = shallow_clone(
        token=installation.token,
        owner=owner,
        repo=repo,
        branch=metadata.default_branch,
        destination=workspace.repository / repo,
        max_size_bytes=500 * 1024 * 1024,
    )

    repository_path = Path(clone_result["path"])

    source_inventory = scan_source_files(repository_path)
    manifests = find_manifests(repository_path)
    project = detect_project(repository_path, source_inventory, manifests)
    languages = detect_languages(
        source_inventory,
        github_languages=metadata.languages,
    )
    frameworks = detect_frameworks(
        repository_path,
        languages,
        manifests,
    )

    manifest = build_repository_manifest(
        metadata=metadata,
        job_id=job_id,
        clone_result=clone_result,
        source_inventory=source_inventory,
        manifests=manifests,
        project=project,
        languages=languages,
        frameworks=frameworks,
    )

    write_json(workspace.metadata / "repository_manifest.json", manifest)
    write_json(
        workspace.metadata / "source_inventory.json",
        source_inventory,
    )

    return manifest


def _parse_github_url(repo_url: str) -> tuple[str, str]:
    from urllib.parse import urlparse

    parsed = urlparse(repo_url)

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http and https GitHub URLs are allowed.")

    if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
        raise ValueError("Only github.com repository URLs are accepted.")

    parts = [part for part in parsed.path.split("/") if part]

    if len(parts) < 2:
        raise ValueError("Invalid GitHub repository URL.")

    owner = parts[0]
    repo = parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]

    if not owner or not repo:
        raise ValueError("Invalid GitHub owner/repository.")

    return owner, repo
