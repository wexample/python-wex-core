from typing import Type, TYPE_CHECKING, Optional, List

from wexample_app.common.abstract_kernel import AbstractKernel
from wexample_app.common.mixins.command_line_kernel import CommandLineKernel
from wexample_app.common.mixins.command_runner_kernel import CommandRunnerKernel
from wexample_prompt.enums.verbosity_level import VerbosityLevel
from wexample_wex_core.resolver.addon_command_resolver import AddonCommandResolver

if TYPE_CHECKING:
    from wexample_app.resolver.abstract_command_resolver import AbstractCommandResolver
    from wexample_filestate.file_state_manager import FileStateManager
    from wexample_wex_core.common.abstract_addon_manager import AbstractAddonManager


class Kernel(CommandRunnerKernel, CommandLineKernel, AbstractKernel):
    def __init__(self, **kwargs) -> None:
        AbstractKernel.__init__(self, **kwargs)

    def setup(self, addons: Optional[List[Type["AbstractAddonManager"]]] = None) -> "AbstractKernel":
        response = super().setup()
        self._init_addons(addons=addons)
        self._init_command_line_kernel()
        self._init_resolvers()
        self._init_runners()

        return response

    def _init_addons(self, addons: Optional[List[Type["AbstractAddonManager"]]] = None):
        from wexample_helpers.service.registry import Registry

        self.set_registry("addon", Registry)
        self.register_items("addon", addons or [])

    def _get_command_resolvers(self) -> list[Type["AbstractCommandResolver"]]:
        from wexample_wex_core.resolver.service_command_resolver import ServiceCommandResolver

        return [
            AddonCommandResolver,
            ServiceCommandResolver,
        ]

    def _get_workdir_state_manager_class(self) -> Type["FileStateManager"]:
        from wexample_wex_core.workdir.kernel_workdir import KernelWorkdir

        return KernelWorkdir

    def _get_core_args(self):
        return super()._get_core_args() + [
            {"arg": "quiet", "attr": "verbosity", "value": VerbosityLevel.QUIET},
            {"arg": "vv", "attr": "verbosity", "value": VerbosityLevel.MEDIUM},
            {"arg": "vvv", "attr": "verbosity", "value": VerbosityLevel.MAXIMUM},
        ]
