from typing import Type, Any, TYPE_CHECKING

from wexample_app.common.abstract_kernel import AbstractKernel
from wexample_app.common.mixins.command_line_kernel import CommandLineKernel

if TYPE_CHECKING:
    from wexample_app.common.resolver.abstract_command_resolver import AbstractCommandResolver
    from wexample_filestate.file_state_manager import FileStateManager

class Kernel(AbstractKernel, CommandLineKernel):
    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        self._init_command_line_kernel()

    def _get_command_resolvers(self) -> list[Type["AbstractCommandResolver"]]:
        from wexample_wex_core.resolver.service_command_resolver import ServiceCommandResolver

        return [
            ServiceCommandResolver,
        ]

    def _get_workdir_state_manager_class(self) -> Type["FileStateManager"]:
        from wexample_wex_core.workdir.kernel_workdir import KernelWorkdir

        return KernelWorkdir
