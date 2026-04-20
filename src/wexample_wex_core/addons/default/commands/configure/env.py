from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.decorator.command import command

if TYPE_CHECKING:
    from wexample_wex_core.context.execution_context import ExecutionContext

_CONFIGURABLE_KEYS = [
    {
        "key": "SSH_AUTH_SOCK",
        "description": "SSH agent socket — required for git push/pull over SSH",
        "default_candidates": [
            "/run/user/1000/keyring/ssh",
            "/run/user/1000/gnupg/S.gpg-agent.ssh",
        ],
    },
]


@command(
    type=COMMAND_TYPE_ADDON,
    description="Interactively configure required env vars and persist them to .wex/local/env.yml",
)
def default__configure__env(context: ExecutionContext) -> None:
    import os
    import pathlib

    kernel = context.kernel
    io = context.io

    current_local = kernel.workdir.get_local_data("env")
    updated = dict(current_local)
    changed = False

    for entry in _CONFIGURABLE_KEYS:
        key = entry["key"]
        current_value = os.environ.get(key) or current_local.get(key)
        if current_value:
            io.success(message=f"{key} already set, skipping")
            continue

        auto_detected = next(
            (c for c in entry.get("default_candidates", []) if pathlib.Path(c).is_socket()),
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
        io.success(message="Saved to .wex/local/env.yml")
    else:
        io.log(message="Nothing to save.")
