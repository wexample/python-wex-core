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
    from wexample_wex_core.common.abstract_addon_manager import AbstractAddonManager

    # Change to project root directory
    workdir = context.kernel.workdir.get_resolved()
    os.chdir(workdir)

    for addon in context.kernel.get_addons().values():
        assert isinstance(addon, AbstractAddonManager)
        context.io.log(f'Adding tests from addon: {addon.get_snake_short_class_name()}')

    context.io.log(f"Starting pytest test suite from {workdir}")

    # Build pytest arguments explicitly to avoid using sys.argv
    pytest_args = [
        "tests",  # Run tests from the tests directory
        "--color=yes",  # Enable colored output
        "-v"  # Verbose output
    ]

    context.io.log(f"Running pytest with args: {' '.join(pytest_args)}")

    # Run pytest with explicit arguments
    exit_code = pytest.main(pytest_args)

    if exit_code == 0:
        context.io.success("All tests passed!")
    else:
        context.io.error(f"Tests failed with exit code: {exit_code}")
