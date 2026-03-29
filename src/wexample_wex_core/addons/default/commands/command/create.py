from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command
from wexample_wex_core.decorator.option import option

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext

_TEMPLATES_DIR = Path(__file__).parent / "templates"


def _load_template(command_type: str, extension: str) -> str:
    return (_TEMPLATES_DIR / f"{command_type}.{extension}.tpl").read_text()


@option("force", type=bool, short_name="f", required=False, is_flag=True, default=False, description="Overwrite if exists")
@option("extension", type=str, short_name="e", required=False, default="yml", description="File extension: yml or py")
@option("command", type=str, short_name="c", required=True, description="Command: group/name (user), ~group/name (user), or addon::group/name (addon)")
@command(type=COMMAND_TYPE_ADDON, description="Create a new command file")
def default__command__create(
    context: "ExecutionContext",
    command: str,
    extension: str = "yml",
    force: bool = False,
) -> None:
    import re

    from wexample_app.response.str_response import StrResponse

    if extension not in ("yml", "py"):
        context.io.error(f"Unsupported extension '{extension}'. Use 'yml' or 'py'.")
        return

    # Detect type from command pattern
    addon_match = re.match(r"^([\w-]+)::([\w-]+)/([\w-]+)$", command)
    user_match = re.match(r"^~?([\w-]+)/([\w-]+)$", command)

    if addon_match:
        target, vars = _resolve_addon_target(context, addon_match, extension)
    elif user_match:
        target, vars = _resolve_user_target(user_match, extension)
    else:
        context.io.error(
            f"Invalid command format '{command}'. "
            "Expected: group/name, ~group/name, or addon::group/name"
        )
        return

    if target is None:
        return

    if target.exists() and not force:
        context.io.warning(f"File already exists: {target}  (use --force to overwrite)")
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_load_template(vars["_type"], extension).format(**vars))

    context.io.success(f"Created: {target}")

    # Rebuild registry so the new command is immediately available
    _rebuild_registry(context)

    return StrResponse(kernel=context.kernel, content=str(target))


def _resolve_user_target(
    match: re.Match, extension: str
) -> tuple[Path, dict]:
    group = match.group(1).replace("-", "_")
    name = match.group(2).replace("-", "_")
    target = Path.home() / ".wex" / "commands" / group / f"{name}.{extension}"
    return target, {"_type": "user", "group": group, "name": name}


def _resolve_addon_target(
    context: "ExecutionContext", match: re.Match, extension: str
) -> tuple[Path | None, dict]:
    addon_name = match.group(1).replace("-", "_")
    group = match.group(2).replace("-", "_")
    name = match.group(3).replace("-", "_")

    addons = context.kernel.get_addons()
    if addon_name not in addons:
        context.io.error(
            f"Addon '{addon_name}' not found. "
            f"Available: {sorted(addons.keys())}"
        )
        return None, {}

    addon = addons[addon_name]
    target = addon.workdir.get_path() / "commands" / group / f"{name}.{extension}"
    return target, {"_type": "addon", "addon": addon_name, "group": group, "name": name}


def _rebuild_registry(context: "ExecutionContext") -> None:
    from wexample_app.const.output import OUTPUT_TARGET_NONE
    from wexample_wex_core.common.command_request import CommandRequest

    request = CommandRequest(
        kernel=context.kernel,
        name="default::registry/build",
        arguments={},
        output_target=[OUTPUT_TARGET_NONE],
    )
    context.kernel.execute_kernel_command(request)
