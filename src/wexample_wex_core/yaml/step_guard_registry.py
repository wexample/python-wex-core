from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_helpers.decorator.base_class import base_class
from wexample_helpers.service.singleton_registry import SingletonRegistry

if TYPE_CHECKING:
    from wexample_wex_core.common.kernel import Kernel
    from wexample_wex_core.yaml.abstract_step_guard import AbstractStepGuard


@base_class
class StepGuardRegistry(SingletonRegistry["AbstractStepGuard"]):
    """Registry of YAML step guards contributed by addons."""

    def get_all_step_options(self) -> list[str]:
        """Aggregate valid step keys from all registered guards (for validation)."""
        options: list[str] = []
        for guard in self._items.values():
            options.extend(guard.get_step_options())
        return options

    def should_skip_step(self, step: dict, kernel: Kernel) -> bool:
        """Return True if any guard requests the step to be skipped."""
        return any(guard.should_skip(step, kernel) for guard in self._items.values())
