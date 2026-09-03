from __future__ import annotations

from pathlib import Path


MANIFEST_TYPES = {
    "requirements.txt": "python_requirements",
    "pyproject.toml": "python_project",
    "setup.py": "python_setup",
    "Pipfile": "python_pipenv",
    "poetry.lock": "python_poetry_lock",
    "pom.xml": "maven",
    "build.gradle": "gradle",
    "build.gradle.kts": "gradle_kotlin",
    "settings.gradle": "gradle_settings",
    "settings.gradle.kts": "gradle_settings_kotlin",
    "package.json": "node_package",
    "package-lock.json": "npm_lock",
    "yarn.lock": "yarn_lock",
    "pnpm-lock.yaml": "pnpm_lock",
    "tsconfig.json": "typescript_config",
    "Cargo.toml": "rust_cargo",
    "Cargo.lock": "rust_lock",
    "go.mod": "go_module",
    "go.sum": "go_sum",
    "composer.json": "php_composer",
    "Gemfile": "ruby_bundle",
    "CMakeLists.txt": "cmake",
    "Makefile": "make",
    "meson.build": "meson",
}


def find_manifests(repo_path: Path) -> list[dict]:
    results = []

    for path in repo_path.rglob("*"):
        if not path.is_file():
            continue

        if ".git" in path.parts:
            continue

        manifest_type = MANIFEST_TYPES.get(path.name)
        if not manifest_type:
            continue

        relative = path.relative_to(repo_path)

        results.append(
            {
                "file_name": path.name,
                "path": relative.as_posix(),
                "type": manifest_type,
                "size_bytes": path.stat().st_size,
            }
        )

    return sorted(results, key=lambda x: x["path"])
