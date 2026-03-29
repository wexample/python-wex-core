from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command
from wexample_wex_core.decorator.option import option

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext

_TEMPLATE_YML = (
    'description: ""\n'
    "scripts:\n"
    "  - runner: bash\n"
    '    script: echo "Hello from ~{group}/{name}"\n'
)

_TEMPLATE_PY = (
    "from __future__ import annotations\n"
    "\n"
    "from typing import TYPE_CHECKING\n"
    "\n"
    "from wexample_wex_core.const.globals import COMMAND_TYPE_USER\n"
    "from wexample_wex_core.decorator.command import command\n"
    "\n"
    "if TYPE_CHECKING:\n"
    "    from wexample_wex_core.context.execution_context import ExecutionContext\n"
    "\n"
    "\n"
    '@command(type=COMMAND_TYPE_USER, description="")\n'
    "def user__{group}__{name}(context: \"ExecutionContext\") -> None:\n"
    '    context.io.log("Hello from ~{group}/{name}")\n'
)


@option("force", type=bool, short_name="f", required=False, is_flag=True, default=False, description="Overwrite if exists")
@option("extension", type=str, short_name="e", required=False, default="yml", description="File extension: yml or py")
@option("command", type=str, short_name="c", required=True, description="Command name: group/name or ~group/name")
@command(type=COMMAND_TYPE_ADDON, description="Create a new user command under ~/.wex/commands/")
def default__command__create(
    context: "ExecutionContext",
    command: str,
    extension: str = "yml",
    force: bool = False,
) -> None:
    import re
    from pathlib import Path

    from wexample_app.response.str_response import StrResponse

    command = command.lstrip("~")

    match = re.match(r"^([\w-]+)/([\w-]+)$", command)
    if not match:
        context.io.error(f"Invalid command format '{command}'. Expected: group/name")
        return

    group = match.group(1).replace("-", "_")
    name = match.group(2).replace("-", "_")

    if extension not in ("yml", "py"):
        context.io.error(f"Unsupported extension '{extension}'. Use 'yml' or 'py'.")
        return

    target = Path.home() / ".wex" / "commands" / group / f"{name}.{extension}"

    if target.exists() and not force:
        context.io.warning(f"File already exists: {target}  (use --force to overwrite)")
        return

    target.parent.mkdir(parents=True, exist_ok=True)

    template = _TEMPLATE_YML if extension == "yml" else _TEMPLATE_PY
    target.write_text(template.format(group=group, name=name))

    context.io.success(f"Created: {target}")

    return StrResponse(kernel=context.kernel, content=str(target))
