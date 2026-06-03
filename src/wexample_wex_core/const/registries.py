from __future__ import annotations

from typing import TypedDict

REGISTRY_KERNEL_ADDON: str = "addon"


class RegistryAttachment(TypedDict):
    command: str
    pass_args: bool


class RegistryCommandData(TypedDict):
    alias: list[str]
    attachments: dict[str, list[RegistryAttachment]]
    command: str
    description: str | None
    options: list[dict]
    path: str
    sudo: bool
    tags: list[str]
    test: str | None
    webhook: bool


RegistryAddonData = dict[str, RegistryCommandData]
RegistryResolverData = dict[str, RegistryAddonData]
