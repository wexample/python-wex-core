from typing import Optional

from wexample_filestate.const.enums import DiskItemType
from wexample_filestate.const.types import StateItemConfig
from wexample_filestate.file_state_manager import FileStateManager
from wexample_wex_core.const.globals import WORKDIR_SPECIAL_DIR
from wexample_filestate.const.types_state_items import TargetFileOrDirectory
from wexample_helpers.const.types import FileStringOrPath


class Workdir(FileStateManager):
    def __init__(self, config: Optional[StateItemConfig], **data):
        if "children" not in config:
            config["children"] = []

        config["children"].append({
            "name": WORKDIR_SPECIAL_DIR,
            "type": DiskItemType.DIRECTORY,
            "should_exist": True
        })

        super().__init__(config=config, **data)


Workdir.model_rebuild()
