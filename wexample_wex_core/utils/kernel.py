from typing import Type, Any

from wexample_filestate.file_state_manager import FileStateManager
from wexample_helpers_app.utils.abstract_kernel import AbstractKernel
from wexample_wex_core.core.file.KernelDirectoryStructure import KernelDirectoryStructure
from wexample_helpers_app.utils.mixins.command_line_kernel import CommandLineKernel


class Kernel(AbstractKernel, CommandLineKernel):
    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        self.__init_command_line_kernel()

    def _get_workdir_state_manager_class(self) -> Type[FileStateManager]:
        return KernelDirectoryStructure


    def call(self) -> None:
        """
        Main entrypoint from bash call.
        May never be called by an internal script.
        """

        # No arg found except process id
        if not len(self._sys_argv) > 2:
            return
