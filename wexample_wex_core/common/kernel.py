from typing import Type, Any

from wexample_filestate.file_state_manager import FileStateManager
from wexample_app.utils.abstract_kernel import AbstractKernel
from wexample_wex_core.common.file.kernel_directory_structure import KernelDirectoryStructure
from wexample_app.utils.mixins.command_line_kernel import CommandLineKernel


class Kernel(AbstractKernel, CommandLineKernel):
    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        self._init_command_line_kernel()

    def _get_workdir_state_manager_class(self) -> Type[FileStateManager]:
        return KernelDirectoryStructure
