from typing import TYPE_CHECKING

from pydantic import BaseModel

from wexample_app.common.abstract_kernel_child import AbstractKernelChild
from wexample_helpers.classes.mixin.serializable_mixin import SerializableMixin
from wexample_helpers.const.types import StringKeysDict

if TYPE_CHECKING:
    from wexample_wex_core.common.kernel import Kernel


class KernelRegistry(AbstractKernelChild, SerializableMixin, BaseModel):
    env: str

    def __init__(
            self,
            kernel: "Kernel",
            **kwargs
    ) -> None:
        from wexample_app.const.globals import ENV_VAR_NAME_APP_ENV
        kwargs["env"] = kernel.get_env_parameter(ENV_VAR_NAME_APP_ENV)

        BaseModel.__init__(self, **kwargs)
        AbstractKernelChild.__init__(self, kernel=kernel)
        SerializableMixin.__init__(self)

    def to_dict(self) -> StringKeysDict:
        return {
            "env": self.env
        }
