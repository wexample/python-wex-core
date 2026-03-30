from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper

ATTACH_POSITION_BEFORE = "before"
ATTACH_POSITION_AFTER = "after"


def attach(
    position: str,
    command: str | CommandMethodWrapper,
    pass_args: bool = False,
) -> CommandMethodWrapper:
    """Attach this command to run before or after another command.

    Args:
        position: "before" or "after"
        command: Target command — either a string ("demo::ping/pong") or the
                 CommandMethodWrapper itself (the decorated function object).
        pass_args: If True, forward the target command's arguments to this one
    """

    def decorator(wrapper: CommandMethodWrapper) -> CommandMethodWrapper:
        from wexample_wex_core.common.command_method_wrapper import (
            CommandMethodWrapper as CMW,
        )
        from wexample_wex_core.resolver.abstract_command_resolver import (
            AbstractCommandResolver,
        )

        if isinstance(command, CMW):
            command_name = AbstractCommandResolver.build_command_from_function(command)
        else:
            command_name = command

        wrapper.attachments[position].append(
            {
                "command": command_name,
                "pass_args": pass_args,
            }
        )
        return wrapper

    return decorator
