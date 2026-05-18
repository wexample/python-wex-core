from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper

ATTACH_POSITION_BEFORE = "before"
ATTACH_POSITION_AFTER = "after"
ATTACH_POSITION_ALWAYS_AFTER = "always_after"


def attach(
    position: str,
    command: str | CommandMethodWrapper,
    pass_args: bool = False,
) -> CommandMethodWrapper:
    """Attach this command to run before or after another command.

    Args:
        position: "before", "after", or "always_after".
                  - "before": runs before the target command.
                  - "after": runs after the target command completes normally.
                    Skipped if the command queue stops early.
                  - "always_after": runs after the target command regardless of
                    whether the queue stopped early (like a finally block).
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

        wrapper.attachments.setdefault(position, []).append(
            {
                "command": command_name,
                "pass_args": pass_args,
            }
        )
        return wrapper

    return decorator
