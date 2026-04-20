from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_wex_core.common.kernel import Kernel
    from wexample_wex_core.yaml.abstract_step_guard import AbstractStepGuard


class StepGuardRegistry:
    """Holds addon-registered step guards.

    Guards are checked before each YAML step executes. If any guard returns
    ``True`` from ``should_skip()``, the step is skipped silently.
    """

    def __init__(self) -> None:
        self._guards: list[AbstractStepGuard] = []

    def get_all_step_options(self) -> list[str]:
        """Aggregate valid step keys from all registered guards (for validation)."""
        options: list[str] = []
        for guard in self._guards:
            options.extend(guard.get_step_options())
        return options

    def register(self, guard: AbstractStepGuard) -> None:
        self._guards.append(guard)

    def should_skip_step(self, step: dict, kernel: Kernel) -> bool:
        """Return True if any guard requests the step to be skipped."""
        return any(guard.should_skip(step, kernel) for guard in self._guards)
