from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from tree_sitter import Language, Parser


EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".go": "go",
    ".java": "java",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
}


class ASTGenerator:
    def __init__(self, repo_path: str | Path, output_path: str | Path):
        self.repo_path = Path(repo_path).resolve()
        self.output_path = Path(output_path).resolve()

        self.parsers: Dict[str, Parser] = {}

    def load_language(self, language_name: str):
        """
        Load Tree-sitter language.

        This method assumes language grammar packages are installed
        separately, for example tree-sitter-python, tree-sitter-java, etc.
        """

        if language_name == "python":
            import tree_sitter_python
            return Language(tree_sitter_python.language())

        if language_name == "java":
            import tree_sitter_java
            return Language(tree_sitter_java.language())

        if language_name == "c":
            import tree_sitter_c
            return Language(tree_sitter_c.language())

        if language_name == "cpp":
            import tree_sitter_cpp
            return Language(tree_sitter_cpp.language())

        if language_name == "go":
            import tree_sitter_go
            return Language(tree_sitter_go.language())

        if language_name == "javascript":
            import tree_sitter_javascript
            return Language(tree_sitter_javascript.language())

        if language_name == "typescript":
            import tree_sitter_typescript
            return Language(tree_sitter_typescript.language_typescript())

        if language_name == "tsx":
            import tree_sitter_typescript
            return Language(tree_sitter_typescript.language_tsx())

        raise ValueError(f"Unsupported language: {language_name}")

    def get_parser(self, language_name: str) -> Parser:
        if language_name not in self.parsers:
            language = self.load_language(language_name)

            parser = Parser()
            parser.language = language

            self.parsers[language_name] = parser

        return self.parsers[language_name]

    def detect_language(self, file_path: Path):
        return EXTENSION_TO_LANGUAGE.get(file_path.suffix.lower())

    def parse_file(self, file_path: Path, language_name: str):
        parser = self.get_parser(language_name)

        source = file_path.read_bytes()

        tree = parser.parse(source)

        return source, tree

    def node_to_dict(self, node, source: bytes):
        result = {
            "type": node.type,
            "start_point": {
                "row": node.start_point[0],
                "column": node.start_point[1],
            },
            "end_point": {
                "row": node.end_point[0],
                "column": node.end_point[1],
            },
            "start_byte": node.start_byte,
            "end_byte": node.end_byte,
        }

        children = [
            self.node_to_dict(child, source)
            for child in node.children
        ]

        if children:
            result["children"] = children

        return result

    def generate_for_file(self, file_path: Path):
        language_name = self.detect_language(file_path)

        if not language_name:
            return None

        try:
            source, tree = self.parse_file(
                file_path,
                language_name,
            )

            relative_path = file_path.relative_to(
                self.repo_path
            )

            ast = {
                "file": str(relative_path).replace("\\", "/"),
                "language": language_name,
                "has_errors": tree.root_node.has_error,
                "root": self.node_to_dict(
                    tree.root_node,
                    source,
                ),
            }

            output_file = (
                self.output_path
                / relative_path
            ).with_suffix(
                relative_path.suffix + ".json"
            )

            output_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            output_file.write_text(
                json.dumps(
                    ast,
                    indent=2,
                ),
                encoding="utf-8",
            )

            return ast

        except Exception as exc:
            print(
                f"[ERROR] {file_path}: {exc}"
            )

            return None

    def generate(self):
        if not self.repo_path.exists():
            raise FileNotFoundError(
                f"Repository not found: {self.repo_path}"
            )

        self.output_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        statistics = {
            "total_files": 0,
            "parsed_files": 0,
            "unsupported_files": 0,
            "failed_files": 0,
        }

        for file_path in self.repo_path.rglob("*"):

            if not file_path.is_file():
                continue

            # Don't parse Git internals.
            if ".git" in file_path.parts:
                continue

            statistics["total_files"] += 1

            language = self.detect_language(file_path)

            if not language:
                statistics["unsupported_files"] += 1
                continue

            result = self.generate_for_file(file_path)

            if result is not None:
                statistics["parsed_files"] += 1
            else:
                statistics["failed_files"] += 1

        return statistics
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate Tree-sitter AST JSON files for a repository"
    )

    parser.add_argument(
        "repo_path",
        help="Path to the repository source code"
    )

    parser.add_argument(
        "output_path",
        help="Directory where AST JSON files will be stored"
    )

    args = parser.parse_args()

    generator = ASTGenerator(
        repo_path=args.repo_path,
        output_path=args.output_path,
    )

    statistics = generator.generate()

    print("\nAST generation completed.")
    print(f"Total files:       {statistics['total_files']}")
    print(f"Parsed files:      {statistics['parsed_files']}")
    print(f"Unsupported files: {statistics['unsupported_files']}")
    print(f"Failed files:      {statistics['failed_files']}")