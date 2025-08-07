from typing import TYPE_CHECKING

from pydantic import BaseModel
from wexample_app.common.abstract_kernel_child import AbstractKernelChild
from wexample_wex_core.middleware.abstract_middleware import AbstractMiddleware


class ExecutionPass(
    AbstractKernelChild,
    BaseModel,
):
    middleware: AbstractMiddleware

    def __init__(self, middleware: "AbstractMiddleware", **kwargs):
        BaseModel.__init__(self, **kwargs)
        AbstractKernelChild.__init__(
            self,
            kernel=middleware.kernel
        )
