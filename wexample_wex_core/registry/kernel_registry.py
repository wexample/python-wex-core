from typing import TypedDict

from wexample_helpers.const.types import StringKeysDict


class KernelRegistry(TypedDict):
    env: str
    resolvers: StringKeysDict

    def __init__(self, env: str) -> None:
        super().__init__()
        self.env = env

    def to_dict(self) -> StringKeysDict:
        return vars(self)
