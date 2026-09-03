from __future__ import annotations

import json
from pathlib import Path


def detect_project(
    repo_path: Path,
    source_inventory: dict,
    manifests: list[dict],
) -> dict:
    names = {item["file_name"] for item in manifests}
    languages = set(source_inventory["language_file_counts"])

    project_types = []
    build_systems = []

    if "pyproject.toml" in names or "requirements.txt" in names:
        project_types.append("Python")
    if "pom.xml" in names:
        project_types.append("Java")
        build_systems.append("Maven")
    if "build.gradle" in names or "build.gradle.kts" in names:
        project_types.append("JVM")
        build_systems.append("Gradle")
    if "package.json" in names:
        project_types.append("Node.js")
    if "Cargo.toml" in names:
        project_types.append("Rust")
        build_systems.append("Cargo")
    if "go.mod" in names:
        project_types.append("Go")
        build_systems.append("Go Modules")
    if "CMakeLists.txt" in names:
        build_systems.append("CMake")
        if "cpp" in languages:
            project_types.append("C++")
        elif "c" in languages:
            project_types.append("C")
    if "Makefile" in names:
        build_systems.append("Make")

    if not project_types:
        project_types = sorted(languages)

    # Refine Node.js project type using package.json when safely parseable.
    package_manifest = next(
        (m for m in manifests if m["file_name"] == "package.json"),
        None,
    )
    if package_manifest:
        try:
            data = json.loads(
                (repo_path / package_manifest["path"]).read_text(
                    encoding="utf-8"
                )
            )
            deps = {
                **data.get("dependencies", {}),
                **data.get("devDependencies", {}),
            }
            if "react" in deps:
                project_types.append("React")
            if "next" in deps:
                project_types.append("Next.js")
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            pass

    return {
        "types": sorted(set(project_types)),
        "build_systems": sorted(set(build_systems)),
    }
