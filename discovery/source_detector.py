from __future__ import annotations

from pathlib import Path


LANGUAGE_EXTENSIONS = {
    "python": {".py", ".pyw"},
    "java": {".java"},
    "c": {".c", ".h"},
    "cpp": {".cpp", ".cc", ".cxx", ".hpp", ".hh", ".hxx"},
    "javascript": {".js", ".jsx", ".mjs", ".cjs"},
    "typescript": {".ts", ".tsx"},
    "go": {".go"},
    "rust": {".rs"},
    "php": {".php"},
    "ruby": {".rb"},
    "kotlin": {".kt", ".kts"},
    "swift": {".swift"},
}

IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "vendor",
    "__pycache__",
    ".venv",
    "venv",
    "target",
    "build",
    "dist",
}


def scan_source_files(repo_path: Path) -> dict:
    files = []
    counts = {language: 0 for language in LANGUAGE_EXTENSIONS}

    for path in repo_path.rglob("*"):
        if not path.is_file():
            continue

        relative = path.relative_to(repo_path)

        if any(part in IGNORED_DIRECTORIES for part in relative.parts):
            continue

        language = detect_language_from_extension(path.suffix.lower())
        if not language:
            continue

        size = path.stat().st_size
        entry = {
            "path": relative.as_posix(),
            "file_name": path.name,
            "extension": path.suffix.lower(),
            "language": language,
            "size_bytes": size,
        }

        files.append(entry)
        counts[language] += 1

    return {
        "file_count": len(files),
        "language_file_counts": {
            k: v for k, v in counts.items() if v
        },
        "files": sorted(files, key=lambda x: x["path"]),
    }


def detect_language_from_extension(extension: str) -> str | None:
    for language, extensions in LANGUAGE_EXTENSIONS.items():
        if extension in extensions:
            return language
    return None
