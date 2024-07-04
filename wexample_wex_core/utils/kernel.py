import os
from typing import Dict

from pydantic import BaseModel

from wexample_prompt.io_manager import IOManager


class Kernel(BaseModel):
    def __init__(self, entrypoint_path: str) -> None:
        super().__init__()

        root_path = os.path.dirname(os.path.realpath(entrypoint_path)) + os.sep

        self._path: Dict[str, str] = {
            "root": root_path,
        }

        self.io = IOManager()
