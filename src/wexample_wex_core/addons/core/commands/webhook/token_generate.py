from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command
from wexample_wex_core.decorator.option import option

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext

_VALID_TYPES = ("addon", "service")


@option(
    "type_name",
    type=str,
    required=True,
    description="Webhook type: addon or service",
)
@option(
    "command_name",
    type=str,
    required=False,
    default=None,
    description="Command to secure, e.g. 'app::info/show'",
)
@option(
    "all",
    type=bool,
    is_flag=True,
    required=False,
    default=False,
    description="Generate tokens for all @webhook commands of this type",
)
@option(
    "force",
    type=bool,
    is_flag=True,
    required=False,
    default=False,
    description="Revoke existing token and generate a new one",
)
@command(type=COMMAND_TYPE_ADDON, description="Generate a webhook token for an addon or service command")
def core__webhook__token_generate(
    context: ExecutionContext,
    type_name: str,
    command_name: str | None = None,
    all: bool = False,
    force: bool = False,
) -> None:
    if type_name not in _VALID_TYPES:
        context.io.error(f"--type must be one of: {', '.join(_VALID_TYPES)}")
        return
    if not command_name and not all:
        context.io.error("Specify --command-name <cmd> or --all.")
        return
    if command_name and all:
        context.io.error("--command-name and --all are mutually exclusive.")
        return

    workdir = context.kernel.workdir
    namespace = _namespace(type_name)

    if all:
        webhook_cmds = context.kernel.get_configuration_registry().get_webhook_commands()
        targets = _filter_by_type(webhook_cmds, type_name)
        if not targets:
            context.io.log(f"No @webhook {type_name} commands found.")
            return
    else:
        targets = [command_name]

    for cmd in targets:
        existing = workdir.get_local_data_value(namespace, cmd)
        if existing:
            if not force:
                context.io.warning(f"Token already exists for {cmd} — skipping (use --force).")
                continue
            workdir.delete_local_data_value(namespace, cmd)
        token = workdir.rotate_local_token(namespace, cmd)
        context.io.log(f"Token generated for {cmd}:  @yellow{{{token}}}")


def _namespace(type_name: str) -> str:
    return f"webhook_tokens_{type_name}"


def _filter_by_type(commands: dict, type_name: str) -> list[str]:
    if type_name == "service":
        return [cmd["command"] for cmd in commands.values() if cmd["command"].startswith("@")]
    return [
        cmd["command"]
        for cmd in commands.values()
        if not cmd["command"].startswith(".") and not cmd["command"].startswith("@")
    ]
