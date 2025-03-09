from typing import Optional

from pydantic import BaseModel

from wexample_app.common.abstract_kernel_child import AbstractKernelChild
from wexample_helpers.classes.mixin.has_snake_short_class_name_class_mixin import HasSnakeShortClassNameClassMixin


class AbstractAddonManager(AbstractKernelChild, HasSnakeShortClassNameClassMixin, BaseModel):
    def get_snake_class_name_suffix(cls) -> Optional[str]:
        return "AddonManager"
