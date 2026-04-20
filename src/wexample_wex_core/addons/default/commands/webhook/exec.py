from __future__ import annotations

import re
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urlparse

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command
from wexample_wex_core.decorator.option import option
from wexample_wex_core.webhook.const import WEBHOOK_ROUTES
from wexample_wex_core.webhook.routing import routing_build_command

if TYPE_CHECKING:
    from wexample_app.response.abstract_response import AbstractResponse

    from wexample_wex_core.context.execution_context import ExecutionContext


@option(
    "webhook_path",
    type=str,
    required=True,
    description="Full URL path received by the daemon (including query string)",
)
@command(
    type=COMMAND_TYPE_ADDON,
    description="Internal dispatcher: execute the command targeted by a webhook URL",
)
def default__webhook__exec(
    context: ExecutionContext,
    webhook_path: str,
) -> AbstractResponse | None:
    pass

    parsed = urlparse(webhook_path)
    exec_pattern = WEBHOOK_ROUTES["exec"]["pattern"]
    match = re.match(exec_pattern, parsed.path)

    if not match:
        context.io.error(f"Webhook path does not match exec pattern: {webhook_path}")
        return None

    command_type = match.group(1)  # addon | app | service
    command_path = match.group(2)  # e.g. "app/info/show" or "remote/push_receive"

    # Build wex command string
    command_str = routing_build_command(command_type, command_path)
    if not command_str:
        context.io.error(
            f"Cannot build command from type={command_type} path={command_path}"
        )
        return None

    # Parse query args (first value wins for duplicates, skip reserved _token)
    raw_args = parse_qs(parsed.query)
    arguments: dict = {}
    for key, values in raw_args.items():
        if key.startswith("_"):
            continue  # reserved for meta params (future token, etc.)
        arguments[key] = values[0]

    # For app-type commands, chdir to app_path so AppCommandResolver can walk up
    if command_type == "app" and "app_path" in arguments:
        import os

        app_path = arguments.pop("app_path")
        os.chdir(app_path)

    # Execute the resolved command through the kernel
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
