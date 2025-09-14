from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_app.common.abstract_kernel_child import AbstractKernelChild
from wexample_filestate.mixins.with_workdir_mixin import WithWorkdirMixin
from wexample_helpers.classes.mixin.has_snake_short_class_name_class_mixin import (
    HasSnakeShortClassNameClassMixin,
)
from wexample_helpers.classes.mixin.has_two_steps_init import HasTwoStepInit
from wexample_helpers.decorator.base_class import base_class

if TYPE_CHECKING:
    from wexample_wex_core.middleware.abstract_middleware import AbstractMiddleware


@base_class
class AbstractAddonManager(
    AbstractKernelChild,
    HasTwoStepInit,
    HasSnakeShortClassNameClassMixin,
    WithWorkdirMixin,
):
    def __attrs_post_init__(self) -> None:
        import inspect
        import os.path

        # Get the path of the actual addon manager class file
        manager_file = inspect.getfile(self.__class__)

        self._init_workdir(
            entrypoint_path=os.path.dirname(manager_file),
            io=self.kernel.io,
        )

    @classmethod
    def get_class_name_suffix(cls) -> str | None:
        return "AddonManager"

    def get_middlewares_classes(self) -> list[type[AbstractMiddleware]]:
        return []
