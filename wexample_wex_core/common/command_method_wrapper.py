from pydantic import BaseModel

from wexample_helpers.const.types import AnyCallable


class CommandMethodWrapper(BaseModel):
    function: AnyCallable
