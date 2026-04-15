from __future__ import annotations

import secrets
from pathlib import Path

_NAMESPACE = "webhook_tokens"


def _path(workdir_path: str) -> Path:
    from wexample_app.const.globals import WORKDIR_LOCAL_DIR_NAME, WORKDIR_SETUP_DIR

    return Path(workdir_path) / WORKDIR_SETUP_DIR / WORKDIR_LOCAL_DIR_NAME / f"{_NAMESPACE}.yml"


def _read(workdir_path: str) -> dict:
    from wexample_filestate.item.file.yaml_file import YamlFile

    path = _path(workdir_path)
    if not path.exists():
        return {}
    return YamlFile.create_from_path(path=path).read_parsed()


def _write(workdir_path: str, data: dict) -> None:
    from wexample_filestate.item.file.yaml_file import YamlFile

    path = _path(workdir_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    YamlFile.create_from_path(path=path).write_parsed(data)


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
