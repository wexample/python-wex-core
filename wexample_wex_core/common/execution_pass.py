from pydantic import BaseModel, Field

from wexample_app.common.abstract_kernel_child import AbstractKernelChild
from wexample_helpers.const.types import Kwargs
from wexample_wex_core.middleware.abstract_middleware import AbstractMiddleware


class ExecutionPass(
    AbstractKernelChild,
    BaseModel,
):
    middleware: AbstractMiddleware
    function_kwargs: Kwargs = Field(default_factory=dict)

    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        AbstractKernelChild.__init__(
            self,
            kernel=self.middleware.kernel
        )
