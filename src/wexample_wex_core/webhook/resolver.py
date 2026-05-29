from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class WebhookTypeResolver(Protocol):
    """Resolve command, cwd and token for a given webhook command type.

    One resolver is registered per command type ("app", "addon", "service").
    Core registers none — addons inject their own at daemon startup.
    """

    def build_command(self, command_path: str) -> str | None: ...

    def resolve_cwd(
        self,
        command_path: str,
        query_params: dict[str, list[str]] | None = None,
    ) -> str | None: ...

    def resolve_token(self, command_path: str, command_str: str) -> str | None: ...
