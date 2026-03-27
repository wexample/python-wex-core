from __future__ import annotations

import json
from typing import TYPE_CHECKING, Sequence

from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class

from wexample_app.response.abstract_response import AbstractResponse

if TYPE_CHECKING:
    from wexample_app.const.types import ResponsePrintable


@base_class
class ShellCommandResponse(AbstractResponse):
    """Run a shell command, capture its output, and expose it as a response.

    The command is executed on the first call to get_formatted().
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

    def __attrs_post_init__(self) -> None:
        self._execute_super_attrs_post_init_if_exists()
        self._stdout: str | None = None
        self._returncode: int | None = None

    def _run(self) -> None:
        from wexample_helpers.helpers.shell import shell_run

        result = shell_run(
            self.content,
            cwd=self.workdir,
            capture=True,
            check=not self.ignore_error,
        )
        self._stdout = (result.stdout or "").rstrip("\n")
        self._returncode = result.returncode

    def get_formatted(self, output_format: str) -> str:
        from wexample_app.const.output import OUTPUT_FORMAT_STR

        if self._returncode is None:
            self._run()

        if output_format == OUTPUT_FORMAT_STR:
            return self._stdout or ""

        return json.dumps({"output": self._stdout, "returncode": self._returncode})

    def get_printable(self) -> ResponsePrintable:
        if self._returncode is None:
            self._run()
        return self._stdout or ""
