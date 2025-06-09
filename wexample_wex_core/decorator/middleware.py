from typing import TYPE_CHECKING
from wexample_wex_core.command.middlewares_registry import MiddlewaresRegistry

if TYPE_CHECKING:
    from wexample_helpers.const.types import AnyCallable
    from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper


middlewares_registry = MiddlewaresRegistry()

def middleware(
        name: str,
        **kwargs
) -> "AnyCallable":
    def decorator(command_wrapper: "CommandMethodWrapper") -> "CommandMethodWrapper":
        command_wrapper.set_middleware(middlewares_registry.get_service('middlewares', name))
        return command_wrapper

    return decorator
