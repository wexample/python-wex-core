from __future__ import annotations

import secrets
from pathlib import Path

_TOKEN_FILE = "webhook_tokens.yml"


def _path(workdir_path: str) -> Path:
    return Path(workdir_path) / _TOKEN_FILE


def _read(workdir_path: str) -> dict:
    path = _path(workdir_path)
    if not path.exists():
        return {}
    try:
        import yaml

        with open(path) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def _write(workdir_path: str, data: dict) -> None:
    import yaml

    with open(_path(workdir_path), "w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


def token_store_get(workdir_path: str, command: str) -> str | None:
    """Return the stored token for *command*, or None if none is set."""
    return _read(workdir_path).get(command)


def token_store_set(workdir_path: str, command: str, token: str) -> None:
    """Persist *token* for *command*."""
    data = _read(workdir_path)
    data[command] = token
    _write(workdir_path, data)


def token_store_generate(workdir_path: str, command: str) -> str:
    """Generate and persist a fresh token for *command*, then return it."""
    token = secrets.token_urlsafe(32)
    token_store_set(workdir_path, command, token)
    return token


def token_store_ensure(workdir_path: str, command: str) -> str:
    """Return the existing token for *command*, or generate one if absent."""
    existing = token_store_get(workdir_path, command)
    if existing:
        return existing
    return token_store_generate(workdir_path, command)
