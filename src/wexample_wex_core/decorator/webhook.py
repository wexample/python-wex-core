from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper


def webhook() -> "type[CommandMethodWrapper]":
    """Mark a command as webhook-accessible.

    Sets the ``_wex_webhook`` attribute on the underlying function so the
    webhook system can discover it.  Token generation is explicit via
    ``wex webhook/token-show``.

    Usage::

        @webhook()
        @command(type=COMMAND_TYPE_ADDON)
        def my__group__command(context): ...
    """

    def decorator(wrapper: CommandMethodWrapper) -> CommandMethodWrapper:
        wrapper.webhook = True
        return wrapper

    return decorator  # type: ignore[return-value]
