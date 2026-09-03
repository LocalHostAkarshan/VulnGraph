from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path

import jwt
import requests


GITHUB_API = "https://api.github.com"
GITHUB_GRAPHQL = "https://api.github.com/graphql"


class GitHubAuthError(RuntimeError):
    pass


@dataclass(frozen=True)
class InstallationToken:
    token: str
    expires_at: str


def _read_private_key() -> str:
    """
    Read the GitHub App private key.

    Priority:
    1. GITHUB_PRIVATE_KEY_PATH
    2. GITHUB_PRIVATE_KEY

    GITHUB_PRIVATE_KEY_PATH must contain the path to the .pem file.
    """

    key_path = os.getenv("GITHUB_PRIVATE_KEY_PATH")
    key_value = os.getenv("GITHUB_PRIVATE_KEY")

    # Option 1: PEM supplied directly through environment variable
    if key_value:
        key_value = key_value.replace("\ufeff", "").replace("\\n", "\n").strip()

        if not key_value:
            raise GitHubAuthError(
                "GITHUB_PRIVATE_KEY is set but empty."
            )

        if not key_value.startswith("-----BEGIN") or "PRIVATE KEY-----" not in key_value:
            raise GitHubAuthError(
                "GITHUB_PRIVATE_KEY does not appear to contain a valid PEM private key."
            )

        return key_value

    # Option 2: PEM stored in a file
    if key_path:
        path = Path(key_path).expanduser().resolve()

        if not path.exists():
            raise GitHubAuthError(
                f"GitHub private key does not exist: {path}"
            )

        if not path.is_file():
            raise GitHubAuthError(
                f"GITHUB_PRIVATE_KEY_PATH is not a file: {path}"
            )

        try:
            # utf-8-sig strips a leading BOM automatically if present.
            # Some Windows editors (e.g. Notepad) save .pem files as
            # "UTF-8 with BOM", which inserts an invisible character
            # before "-----BEGIN" and silently breaks PEM parsing
            # further down in PyJWT / cryptography.
            private_key = path.read_text(
                encoding="utf-8-sig"
            ).strip()
        except OSError as exc:
            raise GitHubAuthError(
                f"Unable to read GitHub private key: {path}"
            ) from exc

        if not private_key:
            raise GitHubAuthError(
                f"GitHub private key file is empty: {path}"
            )

        if not private_key.startswith("-----BEGIN") or "PRIVATE KEY-----" not in private_key:
            raise GitHubAuthError(
                f"File does not appear to contain a valid PEM private key: {path}"
            )

        return private_key

    raise GitHubAuthError(
        "GitHub private key configuration missing. "
        "Set GITHUB_PRIVATE_KEY_PATH or GITHUB_PRIVATE_KEY."
    )


def generate_app_jwt() -> str:
    """
    Generate a short-lived JWT for the GitHub App.
    """

    app_id = os.getenv("GITHUB_APP_ID")

    if not app_id:
        raise GitHubAuthError(
            "GITHUB_APP_ID is not set."
        )

    private_key = _read_private_key()

    now = int(time.time())

    payload = {
        "iat": now - 60,
        "exp": now + 540,
        "iss": app_id,
    }

    try:
        encoded = jwt.encode(
            payload,
            private_key,
            algorithm="RS256",
        )

        return encoded

    except Exception as exc:
        raise GitHubAuthError(
            "Failed to generate GitHub App JWT."
        ) from exc


def get_installation_token() -> InstallationToken:
    """
    Exchange the GitHub App JWT for an installation access token.
    """

    installation_id = os.getenv(
        "GITHUB_INSTALLATION_ID"
    )

    if not installation_id:
        raise GitHubAuthError(
            "GITHUB_INSTALLATION_ID is not set."
        )

    app_jwt = generate_app_jwt()

    url = (
        f"{GITHUB_API}/app/installations/"
        f"{installation_id}/access_tokens"
    )

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {app_jwt}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=30,
        )
    except requests.RequestException as exc:
        raise GitHubAuthError(
            f"Failed to connect to GitHub: {exc}"
        ) from exc

    if response.status_code != 201:
        raise GitHubAuthError(
            "Failed to obtain GitHub installation token: "
            f"HTTP {response.status_code}: "
            f"{response.text[:500]}"
        )

    try:
        data = response.json()

        return InstallationToken(
            token=data["token"],
            expires_at=data["expires_at"],
        )

    except (ValueError, KeyError) as exc:
        raise GitHubAuthError(
            "GitHub returned an unexpected installation-token response."
        ) from exc