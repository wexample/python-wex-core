import os
import sys
from typing import Dict

from pydantic import BaseModel

from wexample_prompt.io_manager import IOManager
from wexample_wex_core.core.file.KernelDirectoryStructure import KernelDirectoryStructure


class Kernel(BaseModel):
    _io_manager: IOManager
    _state_manager: KernelDirectoryStructure

    def __init__(self, entrypoint_path: str) -> None:
        super().__init__()
        self._sys_argv: list[str] = sys.argv.copy()

        root_path = os.path.dirname(os.path.realpath(entrypoint_path)) + os.sep

        self._path: Dict[str, str] = {
            "root": root_path,
        }

        self._state_manager = KernelDirectoryStructure.create_from_path(
            path=root_path,
        )

        self._io = IOManager()

    def call(self) -> None:
        """
        Main entrypoint from bash call.
        May never be called by an internal script.
        :return:
        """

        # No arg found except process id
        if not len(self._sys_argv) > 2:
            return
