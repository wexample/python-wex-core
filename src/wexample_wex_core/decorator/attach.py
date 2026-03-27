from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper

ATTACH_POSITION_BEFORE = "before"
ATTACH_POSITION_AFTER = "after"


def attach(
    position: str,
    command: str,
    pass_args: bool = False,
) -> "CommandMethodWrapper":
    """Attach this command to run before or after another command.

    Args:
        position: "before" or "after"
        command: The target command name (e.g. "demo::ping/pong")
        pass_args: If True, forward the target command's arguments to this one
    """
    def decorator(wrapper: CommandMethodWrapper) -> CommandMethodWrapper:
        wrapper.attachments[position].append({
            "command": command,
            "pass_args": pass_args,
        })
        return wrapper

    return decorator
