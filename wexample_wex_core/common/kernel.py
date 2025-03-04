from typing import Type, Any, TYPE_CHECKING

from wexample_app.common.abstract_kernel import AbstractKernel
from wexample_app.common.mixins.command_line_kernel import CommandLineKernel
from wexample_app.common.mixins.command_runner_kernel import CommandRunnerKernel
from wexample_prompt.enums.verbosity_level import VerbosityLevel

if TYPE_CHECKING:
    from wexample_app.resolver.abstract_command_resolver import AbstractCommandResolver
    from wexample_filestate.file_state_manager import FileStateManager


class Kernel(AbstractKernel, CommandRunnerKernel, CommandLineKernel):
    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        self._init_command_line_kernel()
        self._init_resolvers()

    def _get_command_resolvers(self) -> list[Type["AbstractCommandResolver"]]:
        from wexample_wex_core.resolver.service_command_resolver import ServiceCommandResolver

        return [
            ServiceCommandResolver,
        ]

    def _get_workdir_state_manager_class(self) -> Type["FileStateManager"]:
        from wexample_wex_core.workdir.kernel_workdir import KernelWorkdir

        return KernelWorkdir

    def _get_core_args(self):
        return super()._get_core_args() + [
            {"arg": "quiet", "attr": "verbosity", "value": VerbosityLevel.QUIET},
            {"arg": "vv", "attr": "verbosity", "value": VerbosityLevel.MEDIUM},
            {"arg": "vvv", "attr": "verbosity", "value": VerbosityLevel.MAXIMUM},
        ]
