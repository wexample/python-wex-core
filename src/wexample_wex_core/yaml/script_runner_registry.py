from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_wex_core.yaml.abstract_script_runner import AbstractScriptRunner


class ScriptRunnerRegistry:
    """Maps runner names (e.g. ``"bash"``) to ``AbstractScriptRunner`` instances.

    Addons can call ``kernel.script_runner_registry.register(MyRunner)`` to add
    support for new runners (e.g. ``runner: docker``).
    """

    def __init__(self) -> None:
        self._runners: dict[str, AbstractScriptRunner] = {}
        self._register_defaults()

    def all(self) -> dict[str, AbstractScriptRunner]:
        return dict(self._runners)

    def get(self, name: str) -> AbstractScriptRunner | None:
        return self._runners.get(name)

    def register(self, runner: AbstractScriptRunner) -> None:
        self._runners[runner.get_runner_name()] = runner

    def _register_defaults(self) -> None:
        from wexample_wex_core.yaml.runners.bash_script_runner import BashScriptRunner
        from wexample_wex_core.yaml.runners.python_script_runner import (
            PythonScriptRunner,
        )

        self.register(BashScriptRunner())
        self.register(PythonScriptRunner())
