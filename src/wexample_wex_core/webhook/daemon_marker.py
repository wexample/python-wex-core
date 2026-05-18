from __future__ import annotations

from pathlib import Path

MARKER_FILENAME = "webhook.enabled"


def marker_path(workdir: Path | str) -> Path:
    return Path(workdir) / MARKER_FILENAME


def marker_set(workdir: Path | str, port: int) -> None:
    path = marker_path(workdir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{port}\n")


def marker_clear(workdir: Path | str) -> None:
    path = marker_path(workdir)
    if path.exists():
        path.unlink()


def marker_read_port(workdir: Path | str) -> int | None:
    path = marker_path(workdir)
    if not path.exists():
        return None
    content = path.read_text().strip()
    try:
        return int(content)
    except ValueError:
        return None
