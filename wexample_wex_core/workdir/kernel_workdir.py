from typing import Optional

from wexample_config.const.types import DictConfig
from wexample_filestate.const.disk import DiskItemType
from wexample_wex_core.workdir.project_workdir import ProjectWorkdir


class KernelWorkdir(ProjectWorkdir):
    def prepare_value(self, raw_value: Optional[DictConfig] = None) -> DictConfig:
        config = super().prepare_value(
            raw_value=raw_value
        )

        children = raw_value["children"]

        children.append({
            "shortcut": "tmp",
            "name": "tmp",
            "type": DiskItemType.DIRECTORY,
            "should_exist": True
        })

        return config
