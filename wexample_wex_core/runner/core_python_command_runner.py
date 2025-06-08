from typing import TYPE_CHECKING, Optional

from wexample_app.runner.python_command_runner import PythonCommandRunner

if TYPE_CHECKING:
    from wexample_app.common.command import Command
    from wexample_wex_core.common.command_request import CommandRequest


class CorePythonCommandRunner(PythonCommandRunner):
    def build_runnable_command(self, request: "CommandRequest") -> Optional["Command"]:
        from wexample_wex_core.common.command_executor import CommandExecutor
        from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper

        command_wrapper = self._build_command_function(request=request)
        assert isinstance(command_wrapper, CommandMethodWrapper)

        return CommandExecutor(
            kernel=self.kernel,
            command_wrapper=command_wrapper
        )
