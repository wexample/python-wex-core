from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command
from wexample_wex_core.decorator.option import option

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext

_TEMPLATES_DIR = Path(__file__).parent / "templates"


@option(
    "force",
    type=bool,
    short_name="f",
    required=False,
    is_flag=True,
    default=False,
    description="Overwrite if exists",
)
@option(
    "extension",
    type=str,
    short_name="e",
    required=False,
    default="yml",
    description="File extension: yml or py",
)
@option(
    "command",
    type=str,
    short_name="c",
    required=True,
    description="Command: ~group/name (user) or addon::group/name (addon)",
)
@command(type=COMMAND_TYPE_ADDON, description="Create a new command file")
def core__command__create(
    context: ExecutionContext,
    command: str,
    extension: str = "yml",
    force: bool = False,
) -> None:
    from wexample_app.response.str_response import StrResponse

    if extension not in ("yml", "py"):
        context.io.error(f"Unsupported extension '{extension}'. Use 'yml' or 'py'.")
        return

    # group/name without prefix → shorthand for ~group/name
    if "::" not in command and not command.startswith("~"):
        command = f"~{command}"

    # Ask each resolver if it can handle creation for this command string
    result = None
    for resolver in context.kernel.get_resolvers().values():
        result = resolver.build_new_command_target(command, extension)
        if result is not None:
            break

    if result is None:
        context.io.error(
            f"No resolver can create '{command}'. "
            "Use ~group/name for user commands or addon::group/name for addon commands."
        )
        return

    target, vars = result

    if target.exists() and not force:
        context.io.warning(f"File already exists: {target}  (use --force to overwrite)")
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_load_template(vars["_type"], extension).format(**vars))

    context.io.success(f"Created: {target}")

    # Rebuild registry so the new command is immediately available
    from wexample_wex_core.addons.core.commands.registry.build import (
        core__registry__build,
    )

    context.kernel.run_function(core__registry__build)

    return StrResponse(kernel=context.kernel, content=str(target))


def _load_template(command_type: str, extension: str) -> str:
    return (_TEMPLATES_DIR / f"{command_type}.{extension}.tpl").read_text()
