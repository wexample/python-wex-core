from typing import Any

from wexample_app.common.abstract_kernel import AbstractKernel
from wexample_app.common.abstract_kernel_child import AbstractKernelChild
from wexample_config.config_value.config_value import ConfigValue


class RegistryBuilder(AbstractKernelChild, ConfigValue):
    def __init__(self, kernel: "AbstractKernel", **kwargs) -> None:
        ConfigValue.__init__(self, raw={}, **kwargs)
        AbstractKernelChild.__init__(self, kernel=kernel)

    def build(self) -> Any:
        from wexample_app.const.globals import ENV_VAR_NAME_APP_ENV


        return {
            "env": self.kernel.get_env_parameter(ENV_VAR_NAME_APP_ENV)
        }

    def get_str(self, type_check: bool = True) -> str:
        import yaml
        return yaml.dump(self.build())
