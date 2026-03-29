from __future__ import annotations

from typing import TYPE_CHECKING, Any

from wexample_wex_core.yaml.abstract_script_runner import AbstractScriptRunner

if TYPE_CHECKING:
    from wexample_wex_core.common.kernel import Kernel
    from wexample_wex_core.yaml.types import PythonStepDict


class PythonScriptRunner(AbstractScriptRunner):
    @classmethod
    def get_runner_name(cls) -> str:
        return "python"

    @classmethod
    def get_step_options(cls) -> list[str]:
        return super().get_step_options() + ["script", "file"]

    def run(self, step: PythonStepDict, variables: dict[str, str], kernel: Kernel) -> Any:
        from wexample_wex_core.yaml.python_script_response import PythonScriptResponse

        # step strings are already substituted by the time run() is called
        script = step.get("script")
        file = step.get("file")

        if file:
            with open(file) as f:
                script = f.read()

        if not script:
            return None

        return PythonScriptResponse(
            kernel=kernel,
            code=script,
            ignore_error=step.get("ignore_error", False),
            scope={"kernel": kernel},
        )
