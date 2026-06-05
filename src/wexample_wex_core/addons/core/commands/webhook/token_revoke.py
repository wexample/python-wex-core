from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_cli.decorator.command import command
from wexample_cli.decorator.option import option
from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_wex_core.addons.core.const.tags import DomainTag

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext

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
    description="Command whose token should be revoked, e.g. 'app::info/show'",
)
@option(
    "all",
    type=bool,
    is_flag=True,
    required=False,
    default=False,
    description="Revoke tokens for all @webhook commands of this type",
)
@command(
    type=COMMAND_TYPE_ADDON,
    description="Revoke the webhook token for an addon or service command",
    tags=[
        DomainTag.CORE,
        DomainTag.HTTP,
        DomainTag.WEBHOOK,
        EffectTag.DESTRUCTIVE,
        EffectTag.WRITE,
        AudienceTag.DANGEROUS,
        ScopeTag.GLOBAL,
        ScopeTag.LOCAL,
    ],
)
def core__webhook__token_revoke(
    context: ExecutionContext,
    type_name: str,
    command_name: str | None = None,
    all: bool = False,
):
    from wexample_app.response.failure_response import FailureResponse

    if type_name not in _VALID_TYPES:
        return FailureResponse(
            kernel=context.kernel,
            message=f"--type must be one of: {', '.join(_VALID_TYPES)}",
        )
    if not command_name and not all:
        return FailureResponse(
            kernel=context.kernel,
            message="Specify --command-name <cmd> or --all.",
        )
    if command_name and all:
        return FailureResponse(
            kernel=context.kernel,
            message="--command-name and --all are mutually exclusive.",
        )

    workdir = context.kernel.workdir
    namespace = f"webhook_tokens_{type_name}"

    if all:
        webhook_cmds = (
            context.kernel.get_configuration_registry().get_webhook_commands()
        )
        targets = _filter_by_type(webhook_cmds, type_name)
        if not targets:
            return f"No @webhook {type_name} commands found."
    else:
        targets = [command_name]

    for cmd in targets:
        existing = workdir.get_local_data_value(namespace, cmd)
        if not existing:
            context.io.warning(f"No token found for {cmd} — skipping.")
            continue
        workdir.delete_local_data_value(namespace, cmd)
        context.io.log(f"Token revoked for {cmd}.")


def _filter_by_type(commands: dict, type_name: str) -> list[str]:
    if type_name == "service":
        return [
            cmd["command"]
            for cmd in commands.values()
            if cmd["command"].startswith("@")
        ]
    return [
        cmd["command"]
        for cmd in commands.values()
        if not cmd["command"].startswith(".") and not cmd["command"].startswith("@")
    ]
