from __future__ import annotations

from pathlib import Path


class ServiceWebhookTypeResolver:
    """Resolve webhook command and token for service-type URLs.

    URL format: /webhook/service/{service_name}/{command/path}
    Command:    @{service_name}::{command/path}
    Token file: {wex_workdir}/.wex/local/webhook_tokens_service.yml
    """

    def __init__(self, wex_workdir_path: str) -> None:
        self._workdir = Path(wex_workdir_path)

    def build_command(self, command_path: str) -> str | None:
        parsed = self._parse(command_path)
        if parsed is None:
            return None
        service_name, cmd_path = parsed
        return f"@{service_name}::{cmd_path}"

    def resolve_cwd(
        self,
        command_path: str,
        query_params: dict[str, list[str]] | None = None,
    ) -> str | None:
        return None

    def resolve_token(self, command_path: str, command_str: str) -> str | None:
        import yaml
        from wexample_app.const.globals import WORKDIR_LOCAL_DIR_NAME, WORKDIR_SETUP_DIR

        token_file = (
            self._workdir
            / WORKDIR_SETUP_DIR
            / WORKDIR_LOCAL_DIR_NAME
            / "webhook_tokens_service.yml"
        )
        if not token_file.exists():
            return None
        try:
            with open(token_file) as f:
                data = yaml.safe_load(f) or {}
        except Exception:
            return None
        return data.get(command_str)

    def _parse(self, command_path: str) -> tuple[str, str] | None:
        parts = command_path.split("/", 1)
        if len(parts) < 2:
            return None
        return parts[0], parts[1]
