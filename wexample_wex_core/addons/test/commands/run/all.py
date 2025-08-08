import os
from typing import TYPE_CHECKING

from wexample_wex_core.decorator.command import command

if TYPE_CHECKING:
    from wexample_wex_core.common.execution_context import ExecutionContext


@command()
def test__run__all(
        context: "ExecutionContext"
) -> None:
    import pytest

    # Change to project root directory
    workdir = context.kernel.workdir.get_resolved()
    os.chdir(workdir)

    context.io.log(f"Starting pytest test suite from {workdir}")

    # Run pytest and capture the exit code
    exit_code = pytest.main()

    if exit_code == 0:
        context.io.success("All tests passed!")
    else:
        context.io.error(f"Tests failed with exit code: {exit_code}")
