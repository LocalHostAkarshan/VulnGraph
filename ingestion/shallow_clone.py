from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


class CloneError(RuntimeError):
    pass


def _directory_size(path: Path) -> int:
    total = 0
    for item in path.rglob("*"):
        if item.is_file() and not item.is_symlink():
            try:
                total += item.stat().st_size
            except OSError:
                pass
    return total


def shallow_clone(
    token: str,
    owner: str,
    repo: str,
    branch: str,
    destination: Path,
    max_size_bytes: int,
) -> dict:
    destination = destination.resolve()

    if destination.exists():
        raise CloneError(f"Clone destination already exists: {destination}")

    destination.parent.mkdir(parents=True, exist_ok=True)

    # Avoid putting the GitHub token in the clone URL or command line.
    with tempfile.TemporaryDirectory(prefix="repo-auditor-askpass-") as tmp:
        tmp_path = Path(tmp)
        askpass = tmp_path / "askpass.py"

        askpass.write_text(
            """import os
import sys
prompt = sys.argv[1].lower() if len(sys.argv) > 1 else ""
if "username" in prompt:
    print("x-access-token")
else:
    print(os.environ["REPO_AUDITOR_GITHUB_TOKEN"])
""",
            encoding="utf-8",
        )

        env = os.environ.copy()
        env["REPO_AUDITOR_GITHUB_TOKEN"] = token
        env["GIT_ASKPASS"] = str(askpass)
        env["GIT_TERMINAL_PROMPT"] = "0"

        url = f"https://github.com/{owner}/{repo}.git"

        try:
            subprocess.run(
                [
                    "git",
                    "-c", "credential.helper=",
                    "clone",
                    "--depth", "1",
                    "--single-branch",
                    "--branch", branch,
                    url,
                    str(destination),
                ],
                env=env,
                check=True,
                capture_output=True,
                text=True,
                timeout=300,
            )
        except FileNotFoundError as exc:
            raise CloneError("Git is not installed or not on PATH.") from exc
        except subprocess.TimeoutExpired as exc:
            shutil.rmtree(destination, ignore_errors=True)
            raise CloneError("Git clone timed out.") from exc
        except subprocess.CalledProcessError as exc:
            shutil.rmtree(destination, ignore_errors=True)
            # Do not include stdout/stderr because authentication material can
            # accidentally be echoed by Git or helpers.
            raise CloneError(
                f"Shallow clone failed with exit code {exc.returncode}."
            ) from exc

    actual_size = _directory_size(destination)

    if actual_size > max_size_bytes:
        shutil.rmtree(destination, ignore_errors=True)
        raise CloneError(
            f"Cloned snapshot exceeds size limit: "
            f"{actual_size:,} > {max_size_bytes:,} bytes."
        )

    return {
        "path": str(destination),
        "clone_depth": 1,
        "history_downloaded": False,
        "size_bytes": actual_size,
    }
