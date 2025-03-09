from wexample_config.const.types import DictConfig
from wexample_filestate.file_state_manager import FileStateManager
from wexample_helpers.const.types import *


class Workdir(FileStateManager):
    should_exist: bool = True

    def prepare_value(self, config: Optional[DictConfig] = None) -> DictConfig:
        from wexample_wex_core.const.globals import WORKDIR_SETUP_DIR
        from wexample_filestate.const.disk import DiskItemType

        config = super().prepare_value(config)

        if "children" not in config:
            config["children"] = []

        config["children"].append({
            "name": WORKDIR_SETUP_DIR,
            'type': DiskItemType.DIRECTORY,
            'should_exist': True,
        })

        return config
