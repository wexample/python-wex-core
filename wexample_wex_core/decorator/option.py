from typing import TYPE_CHECKING

from wexample_helpers.const.types import Args, Kwargs

if TYPE_CHECKING:
    from wexample_helpers.const.types import AnyCallable


# Define your custom decorator
def option(*args: Args, **kwargs: Kwargs) -> "AnyCallable":
    def decorator(function: AnyCallable) -> "AnyCallable":
        # TODO attach options
        return function

    return decorator
