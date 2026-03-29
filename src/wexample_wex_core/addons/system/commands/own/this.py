from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.as_sudo import as_sudo
from wexample_wex_core.decorator.command import command
from wexample_wex_core.decorator.option import option

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext


def _get_real_user() -> str:
    """Return the real user, even when called via sudo."""
    return os.environ.get("SUDO_USER") or os.environ.get("USER") or os.getlogin()


def _chown_recursively(path: Path, uid: int, gid: int) -> None:
    os.chown(path, uid, gid)
    for entry in path.rglob("*"):
        try:
            os.chown(entry, uid, gid)
        except OSError:
            pass


@option("path", type=str, short_name="p", required=False, default=None, description="Path to own (default: cwd)")
@as_sudo()
@command(type=COMMAND_TYPE_ADDON, description="Make current user owner of a directory recursively")
def system__own__this(context: "ExecutionContext", path: Optional[str] = None) -> None:
    import grp
    import pwd

    target = Path(path) if path else Path(os.getcwd())
    username = _get_real_user()

    pw = pwd.getpwnam(username)
    uid, gid = pw.pw_uid, pw.pw_gid

    context.io.log(f'Setting ownership to "{username}" on: {target}')
    _chown_recursively(target, uid, gid)
    context.io.success(f"Done")
