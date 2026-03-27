from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class

from wexample_app.response.abstract_response import AbstractResponse

if TYPE_CHECKING:
    from wexample_app.const.types import ResponsePrintable


@base_class
class InteractiveShellCommandResponse(AbstractResponse):
    """Run a shell command with live stdio passthrough (no output capture).

    stdout/stderr go directly to the terminal; get_formatted() returns "".
    """

    content: list[str] | str = public_field(
        description="Command to execute as a list of args or a shell string"
    )
    ignore_error: bool = public_field(
        default=False,
        description="If True, do not raise on non-zero exit code",
    )
    workdir: str | None = public_field(
        default=None,
        description="Working directory for the command",
    )

    def get_formatted(self, output_format: str) -> str:
        from wexample_helpers.helpers.shell import shell_run

        shell_run(
            self.content,
            cwd=self.workdir,
            capture=False,
            inherit_stdio=True,
            check=not self.ignore_error,
        )
        return ""

    def get_printable(self) -> ResponsePrintable:
        return None
