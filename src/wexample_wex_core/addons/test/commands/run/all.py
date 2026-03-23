from __future__ import annotations

import os
from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext


@command(type=COMMAND_TYPE_ADDON)
def test__run__all(context: ExecutionContext) -> None:
    import pytest

    workdir = context.kernel.workdir.get_path()
    os.chdir(workdir)

    context.io.log(f"Starting pytest test suite from {workdir}")

    addon_commands = context.kernel.get_configuration_registry().get_addon_commands()
    test_paths: list[str] = []
    missing_tests: list[str] = []

    for commands in addon_commands.values():
        for cmd_entry in commands.values():
            if cmd_entry["test"]:
                test_paths.append(cmd_entry["test"])
            else:
                missing_tests.append(cmd_entry["command"])

    project_tests = str(workdir / "tests")
    if os.path.isdir(project_tests) and project_tests not in test_paths:
        test_paths.insert(0, project_tests)

    if missing_tests:
        context.io.log(f"{len(missing_tests)} command(s) have no test file:")
        for cmd in missing_tests:
            context.io.log(f"  - {cmd}", indentation=1)

    context.io.log(f"Running pytest across {len(test_paths)} path(s)...")
    exit_code = pytest.main([*test_paths, "--color=yes", "-v"])

    if exit_code == 0:
        context.io.success("All tests passed!")
    else:
        context.io.error(f"Tests failed with exit code: {exit_code}")
