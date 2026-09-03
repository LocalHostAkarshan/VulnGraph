from __future__ import annotations


def detect_languages(
    source_inventory: dict,
    github_languages: list[dict],
) -> list[dict]:
    files = source_inventory["files"]

    by_language = {}
    for item in files:
        language = item["language"]
        record = by_language.setdefault(
            language,
            {
                "name": language,
                "file_count": 0,
                "source_bytes": 0,
                "extensions": set(),
            },
        )
        record["file_count"] += 1
        record["source_bytes"] += item["size_bytes"]
        record["extensions"].add(item["extension"])

    total_bytes = sum(x["source_bytes"] for x in by_language.values())

    github_bytes = {
        item["name"]: item.get("bytes", 0)
        for item in github_languages
    }

    results = []
    for item in by_language.values():
        item["extensions"] = sorted(item["extensions"])
        item["percentage"] = (
            round(item["source_bytes"] * 100 / total_bytes, 2)
            if total_bytes else 0.0
        )
        item["github_reported_bytes"] = github_bytes.get(
            _normalize(item["name"]),
            0,
        )
        results.append(item)

    return sorted(
        results,
        key=lambda x: x["source_bytes"],
        reverse=True,
    )


def _normalize(value: str) -> str:
    mapping = {
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "python": "Python",
        "java": "Java",
        "c": "C",
        "cpp": "C++",
        "go": "Go",
        "rust": "Rust",
        "php": "PHP",
        "ruby": "Ruby",
        "kotlin": "Kotlin",
        "swift": "Swift",
    }
    return mapping.get(value.lower(), value)
