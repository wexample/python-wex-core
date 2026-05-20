from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_helpers.service.registrable import Registrable

    from wexample_wex_core.common.kernel import Kernel


class AbstractStepGuard(ABC):
    """Intercepts YAML step execution to conditionally skip a step.

    Addons register subclasses via ``AbstractAddonManager.get_step_guard_classes()``.
    Each guard declares the step keys it handles (for validation) and decides
    whether a given step should be skipped.
    """

    @classmethod
    def dependencies(cls) -> list[type[Registrable]]:
        return []

    # ------------------------------------------------------------------
    # Registrable Protocol
    # ------------------------------------------------------------------
    @classmethod
    def get_registry_key(cls) -> str:
        return cls.__name__

    @classmethod
    def get_step_options(cls) -> list[str]:
        """Return step keys introduced by this guard.

        Listed keys are added to the set of valid step options so the YAML
        validator does not reject them. Subclasses should return every key
        they read from the step dict.
        """
        return []

    async def init_async(self) -> None:
        return None

    def init_sync(self) -> None:
        return None

    @abstractmethod
    def should_skip(self, step: dict, kernel: Kernel) -> bool:
        """Return True if the step should be skipped, False to let it run."""
