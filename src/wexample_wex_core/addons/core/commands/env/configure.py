from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_cli.decorator.command import command

from wexample_wex_core.addons.core.const.tags import DomainTag
from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext

_CONFIGURABLE_KEYS: list[dict] = []


@command(
    type=COMMAND_TYPE_ADDON,
    description="Interactively configure required env vars and persist them to .wex/local/env.yml",
    tags=[
        DomainTag.CORE,
        DomainTag.ENV,
        EffectTag.WRITE,
        AudienceTag.REQUIRES_CONFIRMATION,
        ScopeTag.LOCAL,
        ScopeTag.NO_CONTEXT,
    ],
)
def core__env__configure(context: ExecutionContext):
    import os
    import pathlib

    from wexample_app.response.success_response import SuccessResponse

    kernel = context.kernel
    io = context.io

    current_local = kernel.workdir.get_local_data("env")
    updated = dict(current_local)
    changed = False

    addon_keys = []
    for addon in kernel.get_addons().values():
        addon_keys.extend(addon.get_local_configurable_keys())

    for entry in _CONFIGURABLE_KEYS + addon_keys:
        key = entry["key"]
        current_value = os.environ.get(key) or current_local.get(key)
        if current_value:
            io.success(message=f"{key} already set, skipping")
            continue

        auto_detected = next(
            (
                c
                for c in entry.get("default_candidates", [])
                if pathlib.Path(c).is_socket()
            ),
            None,
        )
        io.log(message=entry["description"])
        value = io.input(
            question=f"Value for {key}:",
            default_value=auto_detected,
        ).get_value()
        if value:
            updated[key] = value
            os.environ[key] = value
            changed = True
        else:
            io.warning(message=f"{key} skipped — left unset")

    if changed:
        kernel.workdir.set_local_data("env", updated)
        return SuccessResponse(
            kernel=context.kernel, message="Saved to .wex/local/env.yml"
        )
    return "Nothing to save."
