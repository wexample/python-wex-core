from typing import Optional, TYPE_CHECKING, List, Type, Dict, Any, Union

from pydantic import BaseModel, Field

from wexample_helpers.classes.mixin.has_class_dependencies import HasClassDependencies
from wexample_helpers.classes.mixin.has_snake_short_class_name_class_mixin import HasSnakeShortClassNameClassMixin
from wexample_helpers.classes.mixin.has_two_steps_init import HasTwoStepInit

if TYPE_CHECKING:
    from wexample_helpers.const.types import Kwargs
    from wexample_wex_core.command.option import Option


class OptionDefinition(BaseModel):
    """Definition of a command option for middleware."""
    name: str
    type: Type
    required: bool = False
    description: Optional[str] = None
    default: Any = None


class AbstractMiddleware(
    HasSnakeShortClassNameClassMixin,
    HasTwoStepInit,
    HasClassDependencies,
    BaseModel
):
    options: List[Union[Dict[str, Any], OptionDefinition]] = Field(default_factory=list)

    @classmethod
    def get_class_name_suffix(cls) -> Optional[str]:
        return 'Middleware'

    def build_execution_passes(self, function_kwargs: "Kwargs") -> List["Kwargs"]:
        return [
            function_kwargs
        ]

    def build_options(self) -> List["Option"]:
        from wexample_wex_core.command.option import Option

        """Convert options from various formats to OptionDefinition objects."""
        normalized = []

        for option in self.options:
            if isinstance(option, dict):
                normalized.append(Option(**option))
            elif isinstance(option, Option):
                normalized.append(option)
            else:
                raise TypeError(f"Unsupported option type: {type(option)}")

        return normalized
