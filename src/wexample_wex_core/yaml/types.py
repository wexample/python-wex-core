from __future__ import annotations

from typing import TypedDict


class BaseStepDict(TypedDict, total=False):
    """Keys valid on every script step regardless of runner."""

    ignore_error: bool
    runner: str
    variable: str


class BashStepDict(BaseStepDict, total=False):
    file: str
    script: str
    workdir: str


class PythonStepDict(BaseStepDict, total=False):
    file: str
    script: str


class InternalCommandStepDict(TypedDict, total=False):
    """Step that calls another wex command internally."""

    args: dict
    command: str
    variable: str
