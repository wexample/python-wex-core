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
        middleware_class = middlewares_registry.get_registry('middlewares').get(name)
        command_wrapper.set_middleware(middleware_class(**kwargs))
        return command_wrapper

    return decorator
