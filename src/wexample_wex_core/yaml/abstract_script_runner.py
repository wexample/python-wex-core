from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from wexample_wex_core.common.kernel import Kernel


class AbstractScriptRunner(ABC):
    """Executes a single script step from a YAML command definition."""

    @classmethod
    @abstractmethod
    def get_runner_name(cls) -> str:
        """Return the runner identifier used in the YAML `runner:` field."""

    @classmethod
    def get_step_options(cls) -> list[str]:
        """Declare supported step-level options.

        Used for documentation and YAML validation.
        Subclasses should call ``super().get_step_options() + [...]``.
        """
        return ["ignore_error"]

    @abstractmethod
    def run(self, step: dict, variables: dict[str, str], kernel: Kernel) -> Any:
        """Execute the step and return a response (or None)."""
