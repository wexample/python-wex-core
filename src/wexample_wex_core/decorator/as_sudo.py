from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper


def as_sudo() -> "CommandMethodWrapper":
    def decorator(wrapper: "CommandMethodWrapper") -> "CommandMethodWrapper":
        wrapper.sudo = True
        return wrapper

    return decorator
