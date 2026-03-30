from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_app.response.abstract_response import AbstractResponse
from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class

if TYPE_CHECKING:
    from wexample_app.const.types import ResponsePrintable


@base_class
class PythonScriptResponse(AbstractResponse):
    """Run a Python script lazily on first render, symmetric with ShellCommandResponse."""

    code: str = public_field(description="Python source code to execute")
    ignore_error: bool = public_field(
        default=False,
        description="If True, silently swallow exceptions raised by the script",
    )
    scope: dict = public_field(
        factory=dict,
        description="Variables injected into the script's local scope (kernel, env vars, options)",
    )

    def __attrs_post_init__(self) -> None:
        self._execute_super_attrs_post_init_if_exists()
        self._executed: bool = False
        self._error: Exception | None = None

    def get_formatted(self, output_format: str) -> str:
        if not self._executed:
            self._run()
        if self._error and not self.ignore_error:
            raise self._error
        return ""

    def get_printable(self) -> ResponsePrintable:
        return None

    def _run(self) -> None:
        try:
            exec(self.code, {}, dict(self.scope))  # noqa: S102
        except Exception as exc:
            self._error = exc
        finally:
            self._executed = True
