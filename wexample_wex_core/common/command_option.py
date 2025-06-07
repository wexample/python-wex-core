from typing import Any, Optional, Type

from pydantic import BaseModel


class CommandOption(BaseModel):
    name: str
    type: Type
    description: Optional[str] = None
    required: bool = False
    default: Any = None

    class Config:
        arbitrary_types_allowed = True
