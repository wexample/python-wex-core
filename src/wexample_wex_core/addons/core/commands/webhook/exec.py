from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urlparse

from wexample_cli.decorator.command import command
from wexample_cli.decorator.option import option

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

if TYPE_CHECKING:
    from wexample_app.response.abstract_response import AbstractResponse
    from wexample_cli.context.execution_context import ExecutionContext


@option(
    "command_str",
    type=str,
    required=True,
    description="Resolved wex command string to execute (e.g. '.release/deploy')",
)
@option(
    "webhook_path",
    type=str,
    required=True,
    description="Original URL path from the daemon (used to extract query arguments)",
)
@command(
    type=COMMAND_TYPE_ADDON,
    description="Internal dispatcher: execute a resolved webhook command",
)
def core__webhook__exec(
    context: ExecutionContext,
    command_str: str,
    webhook_path: str,
) -> AbstractResponse | None:
    parsed = urlparse(webhook_path)
    raw_args = parse_qs(parsed.query)
    arguments: dict = {}
    for key, values in raw_args.items():
        if key.startswith("_"):
            continue
        arguments[key] = values[0]

    from wexample_app.const.output import OUTPUT_TARGET_NONE

    from wexample_wex_core.common.command_request import CommandRequest

    request = CommandRequest(
        kernel=context.kernel,
        name=command_str,
        arguments=arguments,
        output_target=[OUTPUT_TARGET_NONE],
    )

    context.io.log(f"Webhook exec: {command_str}  args={arguments}")

    return context.kernel.execute_kernel_command(request)
