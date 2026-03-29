from __future__ import annotations

from typing import TYPE_CHECKING, Any

from wexample_wex_core.yaml.abstract_script_runner import AbstractScriptRunner

if TYPE_CHECKING:
    from wexample_wex_core.common.kernel import Kernel


class PythonScriptRunner(AbstractScriptRunner):
    @classmethod
    def get_runner_name(cls) -> str:
        return "python"

    def run(self, step: dict, variables: dict[str, str], kernel: Kernel) -> Any:
        from wexample_wex_core.yaml.yaml_variable import yaml_substitute

        script = step.get("script")
        file = step.get("file")

        if file:
            with open(yaml_substitute(file, variables)) as f:
                script = f.read()

        if script:
            exec(yaml_substitute(script, variables), {"kernel": kernel, **variables})  # noqa: S102

        return None
