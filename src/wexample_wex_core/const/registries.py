from __future__ import annotations

from typing import TypedDict

REGISTRY_KERNEL_ADDON: str = "addon"


class RegistryAttachment(TypedDict):
    command: str
    pass_args: bool


class RegistryCommandData(TypedDict):
    command: str
    path: str
    test: str | None
    description: str | None
    alias: list[str]
    attachments: dict[str, list[RegistryAttachment]]
    sudo: bool


RegistryAddonData = dict[str, RegistryCommandData]
RegistryResolverData = dict[str, RegistryAddonData]
