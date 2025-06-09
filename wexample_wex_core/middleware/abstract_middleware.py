from typing import Optional

from pydantic import BaseModel

from wexample_helpers.classes.mixin.has_class_dependencies import HasClassDependencies
from wexample_helpers.classes.mixin.has_snake_short_class_name_class_mixin import HasSnakeShortClassNameClassMixin
from wexample_helpers.classes.mixin.has_two_steps_init import HasTwoStepInit


class AbstractMiddleware(
    HasSnakeShortClassNameClassMixin,
    HasTwoStepInit,
    HasClassDependencies,
    BaseModel
):
    @classmethod
    def get_class_name_suffix(cls) -> Optional[str]:
        return 'Middleware'
