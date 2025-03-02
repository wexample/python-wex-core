from typing import Type, Any, TYPE_CHECKING

from wexample_app.utils.abstract_kernel import AbstractKernel
from wexample_app.utils.mixins.command_line_kernel import CommandLineKernel

if TYPE_CHECKING:
    from utils.abstract_command_resolver import AbstractCommandResolver
    from wexample_filestate.file_state_manager import FileStateManager
    from wexample_wex_core.common.file.kernel_directory_structure import KernelDirectoryStructure

class Kernel(AbstractKernel, CommandLineKernel):
    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        self._init_command_line_kernel()

    def _get_command_resolvers(self) -> list[Type["AbstractCommandResolver"]]:
        from wexample_wex_core.common.resolver.service_command_resolver import ServiceCommandResolver

        return [
            ServiceCommandResolver,
        ]

    def _get_workdir_state_manager_class(self) -> Type["FileStateManager"]:
        from wexample_wex_core.common.file.kernel_directory_structure import KernelDirectoryStructure

        return KernelDirectoryStructure
