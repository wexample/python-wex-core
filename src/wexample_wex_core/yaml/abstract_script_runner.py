from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from wexample_helpers.service.registrable import Registrable

    from wexample_wex_core.common.kernel import Kernel


class AbstractScriptRunner(ABC):
    """Executes a single script step from a YAML command definition."""

    @classmethod
    @abstractmethod
    def get_runner_name(cls) -> str:
        """Return the runner identifier used in the YAML `runner:` field."""

    @classmethod
    def get_step_options(cls) -> list[str]:
        """Declare all valid keys for this runner's steps.

        Used for YAML validation — any key not listed here triggers an error.
        Structural keys (``runner``, ``variable``) are always valid and need
        not be listed here.
        Subclasses should call ``super().get_step_options() + [...]``.
        """
        return ["ignore_error", "name"]

    @abstractmethod
    def run(self, step: dict, variables: dict[str, str], kernel: Kernel) -> Any:
        """Execute the step and return a response (or None)."""

    # ------------------------------------------------------------------
    # Registrable Protocol
    # ------------------------------------------------------------------

    @classmethod
    def get_registry_key(cls) -> str:
        return cls.get_runner_name()

    @classmethod
    def dependencies(cls) -> list[type[Registrable]]:
        return []

    def init_sync(self) -> None:
        return None

    async def init_async(self) -> None:
        return None
