"""Load a local env file without overriding variables already set in the process."""

from __future__ import annotations

import os
from pathlib import Path


def load_local_env(repo_root: Path) -> None:
    for path in (repo_root / ".env", repo_root / "backend" / ".env"):
        _load_file(path)


def _load_file(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        key, value = _entry(line)
        if key and key not in os.environ:
            os.environ[key] = value


def _entry(line: str) -> tuple[str, str]:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        return "", ""
    key, value = stripped.split("=", 1)
    return key.strip(), value.strip().strip('"').strip("'")
