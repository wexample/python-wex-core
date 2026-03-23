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

    from wexample_wex_core.resolver.addon_command_resolver import AddonCommandResolver

    workdir = context.kernel.workdir.get_path()
    os.chdir(workdir)

    context.io.log(f"Starting pytest test suite from {workdir}")

    # Collect test paths from the addon command registry
    resolvers = context.kernel.get_resolvers()
    addon_resolver = resolvers.get("addon")
    test_paths: list[str] = []
    missing_tests: list[str] = []

    if isinstance(addon_resolver, AddonCommandResolver):
        addon_data = addon_resolver.build_registry_data()

        for addon_name, commands in addon_data.items():
            for command_key, command_entry in commands.items():
                if command_entry["test"]:
                    test_paths.append(command_entry["test"])
                else:
                    missing_tests.append(command_entry["command"])

    # Always include the project-level tests directory if present
    project_tests = str(workdir / "tests")
    if os.path.isdir(project_tests) and project_tests not in test_paths:
        test_paths.insert(0, project_tests)

    if missing_tests:
        context.io.log(f"{len(missing_tests)} command(s) have no test file:")
        for cmd in missing_tests:
            context.io.log(f"  - {cmd}", indentation=1)

    pytest_args = [*test_paths, "--color=yes", "-v"]

    context.io.log(f"Running pytest across {len(test_paths)} path(s)...")
    exit_code = pytest.main(pytest_args)

    if exit_code == 0:
        context.io.success("All tests passed!")
    else:
        context.io.error(f"Tests failed with exit code: {exit_code}")
