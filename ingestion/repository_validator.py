from __future__ import annotations

from dataclasses import dataclass

from .github_graphql import RepositoryMetadata


MAX_REPOSITORY_SIZE_BYTES = 500 * 1024 * 1024


class RepositoryValidationError(RuntimeError):
    pass


@dataclass(frozen=True)
class ValidationResult:
    accepted: bool
    reason: str


def validate_repository(
    metadata: RepositoryMetadata,
    max_size_bytes: int = MAX_REPOSITORY_SIZE_BYTES,
) -> ValidationResult:
    if metadata.is_archived:
        raise RepositoryValidationError("Archived repositories are not accepted.")

    if metadata.disk_usage_kb is None:
        raise RepositoryValidationError(
            "GitHub did not provide repository disk usage."
        )

    estimated_bytes = metadata.disk_usage_kb * 1024

    if estimated_bytes > max_size_bytes:
        raise RepositoryValidationError(
            f"Repository exceeds the configured limit: "
            f"{estimated_bytes:,} > {max_size_bytes:,} bytes."
        )

    if not metadata.default_branch:
        raise RepositoryValidationError("Repository has no default branch.")

    return ValidationResult(
        accepted=True,
        reason="Repository passed pre-clone validation.",
    )
