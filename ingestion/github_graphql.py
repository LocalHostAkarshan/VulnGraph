from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from .github_auth import GITHUB_GRAPHQL


class GitHubGraphQLError(RuntimeError):
    pass


@dataclass
class RepositoryMetadata:
    id: str
    name: str
    name_with_owner: str
    url: str
    is_private: bool
    is_archived: bool
    is_fork: bool
    disk_usage_kb: int | None
    default_branch: str
    commit_sha: str | None
    languages: list[dict[str, Any]]
    root_entries: list[dict[str, Any]]


QUERY = """
query RepositoryMetadata($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    id
    name
    nameWithOwner
    url
    isPrivate
    isArchived
    isFork
    diskUsage

    defaultBranchRef {
      name
      target {
        oid
      }
    }

    languages(first: 20, orderBy: {field: SIZE, direction: DESC}) {
      edges {
        size
        node {
          name
        }
      }
    }

    object(expression: "HEAD:") {
      ... on Tree {
        entries {
          name
          type
        }
      }
    }
  }
}
"""


def fetch_repository_metadata(
    token: str,
    owner: str,
    repo: str,
) -> RepositoryMetadata:
    response = requests.post(
        GITHUB_GRAPHQL,
        json={
            "query": QUERY,
            "variables": {"owner": owner, "name": repo},
        },
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        timeout=30,
    )

    if response.status_code != 200:
        raise GitHubGraphQLError(
            f"GraphQL HTTP error {response.status_code}: "
            f"{response.text[:500]}"
        )

    payload = response.json()

    if payload.get("errors"):
        messages = "; ".join(
            error.get("message", "Unknown GraphQL error")
            for error in payload["errors"]
        )
        raise GitHubGraphQLError(messages)

    repository = payload.get("data", {}).get("repository")
    if repository is None:
        raise GitHubGraphQLError("Repository not found or not accessible.")

    branch = repository.get("defaultBranchRef") or {}
    target = branch.get("target") or {}

    languages = []
    for edge in (repository.get("languages") or {}).get("edges", []):
        node = edge.get("node") or {}
        languages.append(
            {
                "name": node.get("name"),
                "bytes": edge.get("size", 0),
            }
        )

    root_entries = []
    for entry in (repository.get("object") or {}).get("entries", []):
        root_entries.append(
            {
                "name": entry.get("name"),
                "type": entry.get("type"),
            }
        )

    return RepositoryMetadata(
        id=repository["id"],
        name=repository["name"],
        name_with_owner=repository["nameWithOwner"],
        url=repository["url"],
        is_private=repository["isPrivate"],
        is_archived=repository["isArchived"],
        is_fork=repository["isFork"],
        disk_usage_kb=repository.get("diskUsage"),
        default_branch=branch.get("name") or "HEAD",
        commit_sha=target.get("oid"),
        languages=languages,
        root_entries=root_entries,
    )
