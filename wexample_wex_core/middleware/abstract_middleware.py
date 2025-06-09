from typing import Optional, TYPE_CHECKING, List, Type

from pydantic import BaseModel

from wexample_helpers.classes.mixin.has_class_dependencies import HasClassDependencies
from wexample_helpers.classes.mixin.has_snake_short_class_name_class_mixin import HasSnakeShortClassNameClassMixin
from wexample_helpers.classes.mixin.has_two_steps_init import HasTwoStepInit

if TYPE_CHECKING:
    from wexample_helpers.const.types import Kwargs
    from wexample_wex_core.common.command_option import CommandOption


class AbstractMiddleware(
    HasSnakeShortClassNameClassMixin,
    HasTwoStepInit,
    HasClassDependencies,
    BaseModel
):
    option_name: str
    option_type: Type
    option_required: bool = False

    @classmethod
    def get_class_name_suffix(cls) -> Optional[str]:
        return 'Middleware'

    def build_execution_passes(self, function_kwargs: "Kwargs") -> List["Kwargs"]:
        return [
            function_kwargs
        ]

    def build_options(self) -> List["CommandOption"]:
        return []
