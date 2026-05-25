from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from wexample_cli.decorator.as_sudo import as_sudo
from wexample_cli.decorator.command import command
from wexample_cli.decorator.option import option
from wexample_helpers.helpers.file import file_chown_recursive
from wexample_helpers.helpers.user import user_get_real_username

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext


@option(
    "path",
    type=str,
    short_name="p",
    required=False,
    default=None,
    description="Path to own (default: cwd)",
)
@as_sudo()
@command(
    type=COMMAND_TYPE_ADDON,
    description="Make current user owner of a directory recursively",
)
def system__own__this(context: ExecutionContext, path: str | None = None) -> None:
    import pwd

    target = Path(path) if path else Path(os.getcwd())
    username = user_get_real_username()

    pw = pwd.getpwnam(username)
    uid, gid = pw.pw_uid, pw.pw_gid

    context.io.log(f'Setting ownership to "{username}" on: {target}')
    file_chown_recursive(target, uid, gid)
    context.io.success("Done")
