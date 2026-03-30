from __future__ import annotations

from wexample_wex_core.common.kernel import Kernel


class AppManagerKernel(Kernel):
    def _init_command_line_kernel(self) -> None:
        super()._init_command_line_kernel()
        # The app-manager shell script injects the task ID as sys.argv[1].
        # Skip it by advancing the argv start index past the task ID.
        self._sys_argv_start_index = 2
