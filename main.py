from __future__ import annotations

import argparse
import json

from repo_auditor.ingestion.pipeline import run_repository_ingestion


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Repo Auditor GitHub repository ingestion pipeline."
    )
    parser.add_argument("repo_url")
    parser.add_argument("job_id")

    args = parser.parse_args()

    manifest = run_repository_ingestion(
        repo_url=args.repo_url,
        job_id=args.job_id,
    )

    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
