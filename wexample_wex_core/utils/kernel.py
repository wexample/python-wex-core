import os
import sys
from typing import Dict, Optional

from wexample_helpers_app.utils.abstract_kernel import AbstractKernel
from wexample_wex_core.core.file.KernelDirectoryStructure import KernelDirectoryStructure


class Kernel(AbstractKernel):
    directory: Optional[KernelDirectoryStructure]

    def __init__(self, entrypoint_path: str) -> None:
        super().__init__()
        self._sys_argv: list[str] = sys.argv.copy()

        root_path = os.path.dirname(os.path.realpath(entrypoint_path)) + os.sep

        self._path: Dict[str, str] = {
            "root": root_path,
        }

        self.directory = KernelDirectoryStructure.create_from_path(
            path=root_path,
        )

    def call(self) -> None:
        """
        Main entrypoint from bash call.
        May never be called by an internal script.
        :return:
        """

        # No arg found except process id
        if not len(self._sys_argv) > 2:
            return
