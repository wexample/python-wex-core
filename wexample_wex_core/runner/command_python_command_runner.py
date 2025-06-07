from typing import TYPE_CHECKING, Optional

from wexample_app.common.command import Command
from wexample_app.runner.python_command_runner import PythonCommandRunner
from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper

if TYPE_CHECKING:
    from wexample_wex_core.common.command_request import CommandRequest


class CommandPythonCommandRunner(PythonCommandRunner):
    def will_run(self, request: "CommandRequest") -> bool:
        if super().will_run(request):
            # TODO Check function was wrapped in @command()
            return True
        return False

    def build_runnable_command(self, request: "CommandRequest") -> Optional["Command"]:
        import importlib.util

        command_wrapper = self._load_command_python_function(request=request)

        if not isinstance(command_wrapper, CommandMethodWrapper):
            # TODO Exception
            return None

        # TODO This is temporary, we may need to pass the full wrapper or decopose it here.
        return request.resolver.get_command_class_type()(
            kernel=self.kernel,
            function=command_wrapper.function
        ) if command_wrapper.function is not None else None
