from typing import Any

from wexample_helpers.classes.mixin.has_env_keys import HasEnvKeys
from wexample_app.common.abstract_kernel import AbstractKernel
from wexample_app.common.mixins.command_line_kernel import CommandLineKernel


class Kernel(AbstractKernel, HasEnvKeys, CommandLineKernel):
    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        self._init_command_line_kernel()
