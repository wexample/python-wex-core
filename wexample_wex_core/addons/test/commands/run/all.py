from typing import TYPE_CHECKING

from wexample_wex_core.decorator.command import command

if TYPE_CHECKING:
    from wexample_wex_core.common.execution_context import ExecutionContext


@command()
def test__run__all(
        context: "ExecutionContext"
) -> None:
    context.io.log('Run tests')
