from typing import Any, Optional, Type

from pydantic import BaseModel


class CommandOption(BaseModel):
    name: str
    short_name: Optional[str] = None
    type: Type
    description: Optional[str] = None
    required: bool = False
    default: Any = None
    is_flag: bool = False

    def __init__(self, **kwargs):
        from wexample_wex_core.helpers.option import option_build_short_name

        super().__init__(**kwargs)

        self.short_name = option_build_short_name(self.name)
