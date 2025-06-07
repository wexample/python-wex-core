from typing import TYPE_CHECKING

from wexample_helpers.const.types import Args, Kwargs

if TYPE_CHECKING:
    from wexample_helpers.const.types import AnyCallable
    from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper


# Define your custom decorator
def option(*args: Args, **kwargs: Kwargs) -> "AnyCallable":
    def decorator(command_wrapper: "CommandMethodWrapper") -> "CommandMethodWrapper":
        from wexample_wex_core.common.command_option import CommandOption
        command_wrapper.set_option(CommandOption())
        return command_wrapper

    return decorator
