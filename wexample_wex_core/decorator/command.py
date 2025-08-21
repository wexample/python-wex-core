from typing import TYPE_CHECKING, Optional

from wexample_wex_core.common.command_method_wrapper import \
    CommandMethodWrapper

if TYPE_CHECKING:
    from wexample_helpers.const.types import AnyCallable


def command(description: Optional[str] = None):
    def decorator(function: "AnyCallable"):
        return CommandMethodWrapper(function=function, description=description)

    return decorator
