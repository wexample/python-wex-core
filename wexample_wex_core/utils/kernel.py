from typing import Type, Any

from wexample_filestate.file_state_manager import FileStateManager
from wexample_app.utils.abstract_kernel import AbstractKernel
from wexample_wex_core.core.file.kernel_directory_structure import KernelDirectoryStructure
from wexample_app.utils.mixins.command_line_kernel import CommandLineKernel


class Kernel(AbstractKernel, CommandLineKernel):
    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        self.__init_command_line_kernel()

    def _get_workdir_state_manager_class(self) -> Type[FileStateManager]:
        return KernelDirectoryStructure

    def _get_core_configuration_arguments(self):
        return super()._get_core_configuration_arguments().update([
            # {"arg": "fast-mode", "attr": "fast_mode", "value": True},
            # {"arg": "quiet", "attr": "verbosity", "value": VERBOSITY_LEVEL_QUIET},
            # {"arg": "vv", "attr": "verbosity", "value": VERBOSITY_LEVEL_MEDIUM},
            # {"arg": "vvv", "attr": "verbosity", "value": VERBOSITY_LEVEL_MAXIMUM},
            # {"arg": "log-indent", "attr": "io.log_indent", "cast": int},
            # {"arg": "log-length", "attr": "io.log_length", "cast": int},
            # {"arg": "render-mode", "attr": "default_render_mode", "cast": str},
            # {"arg": "parent-task-id", "attr": "parent_task_id", "cast": str},
            # {"arg": "kernel-task-id", "handler": self.handle_kernel_task_id},
        ])
