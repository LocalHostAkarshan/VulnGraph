from __future__ import annotations

import json
from pathlib import Path


FRAMEWORK_RULES = {
    "python": {
        "fastapi": "FastAPI",
        "django": "Django",
        "flask": "Flask",
        "pytorch": "PyTorch",
        "tensorflow": "TensorFlow",
    },
    "javascript": {
        "react": "React",
        "next": "Next.js",
        "express": "Express",
        "vue": "Vue",
        "angular": "Angular",
    },
    "typescript": {
        "react": "React",
        "next": "Next.js",
        "express": "Express",
        "nestjs": "NestJS",
    },
}


def detect_frameworks(
    repo_path: Path,
    languages: list[dict],
    manifests: list[dict],
) -> list[dict]:
    detected = []
    package_data = _read_package_json(repo_path, manifests)
    package_dependencies = {
        **package_data.get("dependencies", {}),
        **package_data.get("devDependencies", {}),
    }

    py_dependencies = _read_python_dependencies(repo_path, manifests)

    language_names = {item["name"] for item in languages}

    for language in language_names:
        rules = FRAMEWORK_RULES.get(language, {})

        for dependency, framework in rules.items():
            found = False

            if language in {"javascript", "typescript"}:
                found = dependency in package_dependencies

            if language == "python":
                found = dependency.lower() in py_dependencies

            if found:
                detected.append(
                    {
                        "name": framework,
                        "language": language,
                        "confidence": 0.96,
                        "evidence": [
                            f"{dependency} dependency detected"
                        ],
                    }
                )

    return detected


def _read_package_json(repo_path: Path, manifests: list[dict]) -> dict:
    manifest = next(
        (m for m in manifests if m["file_name"] == "package.json"),
        None,
    )
    if not manifest:
        return {}

    try:
        return json.loads(
            (repo_path / manifest["path"]).read_text(encoding="utf-8")
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}


def _read_python_dependencies(
    repo_path: Path,
    manifests: list[dict],
) -> set[str]:
    dependencies = set()

    for manifest in manifests:
        if manifest["file_name"] == "requirements.txt":
            try:
                text = (
                    repo_path / manifest["path"]
                ).read_text(encoding="utf-8")

                for line in text.splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    dependency = (
                        line.split("==")[0]
                        .split(">=")[0]
                        .split("<=")[0]
                        .split("[")[0]
                        .strip()
                        .lower()
                    )
                    dependencies.add(dependency)
            except (OSError, UnicodeDecodeError):
                pass

    return dependencies
