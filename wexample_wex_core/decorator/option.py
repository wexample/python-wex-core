from typing import TYPE_CHECKING

from wexample_helpers.const.types import Args, Kwargs
from wexample_wex_core.exception.command_option_missing_argument_exception import CommandOptionMissingArgumentException

if TYPE_CHECKING:
    from wexample_helpers.const.types import AnyCallable
    from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper


def option(**kwargs: Kwargs) -> "AnyCallable":
    def decorator(command_wrapper: "CommandMethodWrapper") -> "CommandMethodWrapper":
        from wexample_wex_core.common.command_option import CommandOption

        try:
            # Create the CommandOption instance with the provided data
            command_wrapper.set_option(CommandOption(**kwargs))
        except Exception as e:
            raise CommandOptionMissingArgumentException(previous=e)

        return command_wrapper

    return decorator
