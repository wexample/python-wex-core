from wexample_filestate.const.enums import DiskItemType
from wexample_filestate.const.types import StateItemConfig
from wexample_filestate.file_state_manager import FileStateManager
from wexample_helpers.const.types import *
from wexample_wex_core.const.globals import WORKDIR_SETUP_DIR


class Workdir(FileStateManager):

    def prepare_value(self, config: Optional[StateItemConfig] = None) -> StateItemConfig:
        config = super().prepare_value(config)

        if "children" not in config:
            config["children"] = []

        config["children"].append(self.build_setup_config())

        return config or {}

    def build_setup_config(self, config: Optional[StateItemConfig] = None) -> StateItemConfig:
        return {
            "children": [],
            "name": WORKDIR_SETUP_DIR,
            "type": DiskItemType.DIRECTORY,
            "should_exist": True
        }


Workdir.model_rebuild()
