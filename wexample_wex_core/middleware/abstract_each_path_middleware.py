from typing import Optional

from pydantic import BaseModel

from wexample_helpers.classes.mixin.has_snake_short_class_name_class_mixin import HasSnakeShortClassNameClassMixin


class AbstractEachPathMiddleware(HasSnakeShortClassNameClassMixin,BaseModel):
    def get_class_name_suffix(cls) -> Optional[str]:
        return 'Middleware'
