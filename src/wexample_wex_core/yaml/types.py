from __future__ import annotations

from typing import TypedDict


class BaseStepDict(TypedDict, total=False):
    """Keys valid on every script step regardless of runner."""

    runner: str
    variable: str
    ignore_error: bool


class BashStepDict(BaseStepDict, total=False):
    script: str
    file: str
    workdir: str


class PythonStepDict(BaseStepDict, total=False):
    script: str
    file: str


class InternalCommandStepDict(TypedDict, total=False):
    """Step that calls another wex command internally."""

    command: str
    args: dict
    variable: str
