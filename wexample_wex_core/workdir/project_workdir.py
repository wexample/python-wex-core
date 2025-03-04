from wexample_config.const.types import DictConfig
from wexample_filestate.const.disk import DiskItemType
from wexample_filestate_dev.workdir.mixins.with_readme_workdir_mixin import WithReadmeWorkdirMixin
from wexample_filestate_dev.workdir.mixins.with_version_workdir_mixin import WithVersionWorkdirMixin
from wexample_helpers.const.types import *

from wexample_wex_addon_app.const.globals import (
    APP_FILE_APP_CONFIG,
    APP_FILE_APP_ENV, APP_DIR_APP_DATA_NAME,
)
from wexample_wex_core.workdir.workdir import Workdir


class ProjectWorkdir(WithReadmeWorkdirMixin, WithVersionWorkdirMixin, Workdir):
    def prepare_value(self, config: Optional[DictConfig] = None) -> DictConfig:
        from wexample_config.config_value.filter.trim_config_value_filter import TrimConfigValueFilter

        config = super().prepare_value(config)

        config.update({
            "mode": "777",
            "mode_recursive": True,
        })

        children = config["children"]

        self.append_readme(config=config)
        self.append_version(config=config)

        children.append({
            "name": '.gitignore',
            "type": DiskItemType.FILE,
            "should_exist": True,
            "content_filter": TrimConfigValueFilter
        })

        children.append({
            "name": APP_DIR_APP_DATA_NAME,
            "type": DiskItemType.DIRECTORY,
            "should_exist": True,
            "children": [
                {
                    "name": APP_FILE_APP_ENV,
                    "type": DiskItemType.FILE,
                    "should_exist": True
                },
                {
                    "name": APP_FILE_APP_CONFIG,
                    "type": DiskItemType.FILE,
                    "should_exist": True
                },
                {
                    "name": "tmp",
                    "type": DiskItemType.DIRECTORY,
                    "should_exist": True
                }
            ]
        })

        return config
