from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.alias import alias
from wexample_wex_core.decorator.command import command

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext


@alias("rebuild")
@command(type=COMMAND_TYPE_ADDON)
def core__registry__build(context: ExecutionContext) -> None:
    from wexample_wex_core.path.kernel_registry_file import KernelRegistryFile
    from wexample_wex_core.workdir.kernel_workdir import KernelWorkdir

    registry_file = context.kernel.workdir.get_shortcut(KernelWorkdir.SHORTCUT_REGISTRY)
    assert isinstance(registry_file, KernelRegistryFile)

    registry = registry_file.create_registry_and_save(kernel=context.kernel)
    _write_autocomplete_cache(registry, context)
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


def _write_autocomplete_cache(registry, context: ExecutionContext) -> None:
    import json

    serialized = registry.serialize()
    commands: list[str] = []
    aliases: list[str] = []

    for resolver_data in serialized.get("resolvers", {}).values():
        for section_cmds in resolver_data.values():
            for cmd_data in section_cmds.values():
                if not isinstance(cmd_data, dict):
                    continue
                cmd_str = cmd_data.get("command", "")
                if cmd_str:
                    commands.append(cmd_str)
                aliases.extend(cmd_data.get("alias", []))

    cache = {
        "commands": sorted(set(commands)),
        "aliases": sorted(set(aliases)),
    }

    cache_path = context.kernel.workdir.get_path() / "tmp" / "autocomplete.json"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache))
