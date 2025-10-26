from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_helpers.const.types import AnyCallable
    from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper


def middleware(name: str, **kwargs) -> AnyCallable:
    def decorator(command_wrapper: CommandMethodWrapper) -> CommandMethodWrapper:
        # Type safety check
        from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper

        if not isinstance(command_wrapper, CommandMethodWrapper):
            raise TypeError(
                f"Invalid middleware usage: @middleware must decorate a {CommandMethodWrapper.__name__} "
                "object (produced by @command). Make sure @command is applied *before* @middleware."
            )

        command_wrapper.register_middleware(name, kwargs)
        return command_wrapper

    return decorator
