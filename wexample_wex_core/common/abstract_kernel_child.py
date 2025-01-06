from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from wexample_wex_core.common.kernel import Kernel


class AbstractKernelChild(BaseModel):
    kernel: "Kernel"

    def __init__(self, kernel: "Kernel") -> None:
        super().__init__()
        self.kernel = kernel
