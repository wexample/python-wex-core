from wexample_config.config_value.config_value import ConfigValue


class RegistryBuilder(ConfigValue):
    def __init__(self, **data) -> None:
        super().__init__(raw={}, **data)

    def get_str(self, type_check: bool = True) -> str:
        # TODO
        return 'registry: todo'
