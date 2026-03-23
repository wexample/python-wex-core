from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext


@command(type=COMMAND_TYPE_ADDON)
def default__registry__build(context: ExecutionContext) -> None:
    from wexample_wex_core.path.kernel_registry_file import KernelRegistryFile
    from wexample_wex_core.workdir.kernel_workdir import KernelWorkdir

    registry_file = context.kernel.workdir.get_shortcut(KernelWorkdir.SHORTCUT_REGISTRY)
    assert isinstance(registry_file, KernelRegistryFile)

    registry = registry_file.create_registry_and_save(kernel=context.kernel)
    addon_commands = registry.get_addon_commands()

    total_commands = sum(len(cmds) for cmds in addon_commands.values())
    total_with_tests = sum(
        1
        for cmds in addon_commands.values()
        for cmd in cmds.values()
        if cmd.get("test")
    )

    context.io.log(
        f"Registry built: {len(addon_commands)} addon(s), "
        f"{total_commands} command(s), "
        f"{total_with_tests}/{total_commands} with tests"
    )

    for addon_name, commands in sorted(addon_commands.items()):
        context.io.log(f"{addon_name}", indentation=1)
        for cmd_entry in sorted(commands.values(), key=lambda c: c["command"]):
            marker = "✓" if cmd_entry["test"] else "✗"
            context.io.log(f"[{marker}] {cmd_entry['command']}", indentation=2)
