from typing import Mapping

from wexample_helpers.const.types import StringsList

BasicInlineValue = str | int | float | bool | None
CoreCommandArgsDict = Mapping[str, BasicInlineValue]
CoreCommandArgsList = StringsList
