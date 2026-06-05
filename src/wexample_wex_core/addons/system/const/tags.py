"""Domain tags exposed by this addon — one entry per `domain:*` value its commands use."""
from __future__ import annotations


class DomainTag:
    """Functional domain this addon's commands touch."""

    FILESYSTEM = "domain:filesystem"
    PROCESS = "domain:process"
    SYSTEM = "domain:system"
