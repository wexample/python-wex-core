from wexample_config.const.types import DictConfig
from wexample_filestate.file_state_manager import FileStateManager

from wexample_helpers.const.types import *


class Workdir(FileStateManager):
    def prepare_value(self, config: Optional[DictConfig] = None) -> DictConfig:
        config = super().prepare_value(config)

        if "children" not in config:
            config["children"] = []

        return config
