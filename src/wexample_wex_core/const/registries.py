from __future__ import annotations

from typing import TypedDict

REGISTRY_KERNEL_ADDON: str = "addon"


class RegistryCommandData(TypedDict):
    command: str
    path: str
    test: str | None


RegistryAddonData = dict[str, RegistryCommandData]
RegistryResolverData = dict[str, RegistryAddonData]
