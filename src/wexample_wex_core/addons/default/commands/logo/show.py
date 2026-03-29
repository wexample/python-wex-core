from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.alias import alias
from wexample_wex_core.decorator.command import command

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext


@alias("logo")
@command(type=COMMAND_TYPE_ADDON, description="Show the application logo")
def default__logo__show(context: "ExecutionContext"):
    from wexample_app.response.str_response import StrResponse

    logo = context.kernel.get_logo()

    if logo is None:
        context.io.warning("No logo defined for this CLI.")
        return None

    return StrResponse(kernel=context.kernel, content=logo)
