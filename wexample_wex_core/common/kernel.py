from typing import Any

from wexample_app.common.abstract_kernel import AbstractKernel
from wexample_app.common.mixins.command_line_kernel import CommandLineKernel


class Kernel(AbstractKernel, CommandLineKernel):
    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        self._init_command_line_kernel()

    def _get_command_resolvers(self) -> list[Type["AbstractCommandResolver"]]:
        from wexample_wex_core.common.resolver.service_command_resolver import ServiceCommandResolver

        return [
            ServiceCommandResolver,
        ]

    def _get_workdir_state_manager_class(self) -> Type["FileStateManager"]:
        from wexample_wex_core.common.file.kernel_directory_structure import KernelDirectoryStructure

        return KernelDirectoryStructure
