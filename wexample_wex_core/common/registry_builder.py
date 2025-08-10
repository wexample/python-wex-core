from typing import Any

from wexample_config.config_value.config_value import ConfigValue


class RegistryBuilder(ConfigValue):
    def __init__(self, **data) -> None:
        super().__init__(raw={}, **data)

    def build(self) -> Any:
        return {
            "registry": "doing"
        }

    def get_str(self, type_check: bool = True) -> str:
        import yaml
        return yaml.dump(self.build())
