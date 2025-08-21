from typing import Optional, TYPE_CHECKING

from wexample_config.const.types import DictConfig
from wexample_filestate.const.disk import DiskItemType
from wexample_filestate_dev.workdir.mixins.with_readme_workdir_mixin import WithReadmeWorkdirMixin
from wexample_wex_core.workdir.mixin.with_app_version_workdir_mixin import WithAppVersionWorkdirMixin
from wexample_wex_addon_app.const.globals import (
    APP_FILE_APP_CONFIG,
    APP_FILE_APP_ENV, APP_DIR_APP_DATA_NAME,
)
from wexample_wex_core.workdir.workdir import Workdir

if TYPE_CHECKING:
    from wexample_config.config_value.nested_config_value import NestedConfigValue


class ProjectWorkdir(WithReadmeWorkdirMixin, WithAppVersionWorkdirMixin, Workdir):
    def get_config(self) -> "NestedConfigValue":
        from wexample_config.config_value.nested_config_value import NestedConfigValue

        config_yml = self.find_by_name_recursive(item_name=APP_FILE_APP_CONFIG)
        if config_yml:
            return config_yml.read_as_config()

        return NestedConfigValue()

    def prepare_value(self, raw_value: Optional[DictConfig] = None) -> DictConfig:
        from wexample_filestate.config_option.text_filter_config_option import TextFilterConfigOption

        from wexample_filestate.item.file.yaml_file import YamlFile

        raw_value = super().prepare_value(raw_value)

        raw_value.update({
            "mode": "777",
            "mode_recursive": True,
        })

        children = raw_value["children"]

        self.append_readme(config=raw_value)
        self.append_version(config=raw_value)

        children.append({
            "name": '.gitignore',
            "type": DiskItemType.FILE,
            "should_exist": True,
            "text_filter": [
                TextFilterConfigOption.OPTION_NAME_ENSURE_NEWLINE
            ],
        })

        children.append({
            "name": APP_DIR_APP_DATA_NAME,
            "type": DiskItemType.DIRECTORY,
            "should_exist": True,
            "children": [
                {
                    # .env
                    "name": APP_FILE_APP_ENV,
                    "type": DiskItemType.FILE,
                    "should_exist": True,
                    "text_filter": [
                        TextFilterConfigOption.OPTION_NAME_ENSURE_NEWLINE
                    ],
                },
                {
                    # config.yml
                    "name": APP_FILE_APP_CONFIG,
                    "type": DiskItemType.FILE,
                    "should_exist": True,
                    "class": YamlFile,
                    "text_filter": [
                        TextFilterConfigOption.OPTION_NAME_ENSURE_NEWLINE
                    ],
                    "yaml_filter": [
                        "sort_recursive"
                    ],
                },
                {
                    # tmp
                    "name": "tmp",
                    "type": DiskItemType.DIRECTORY,
                    "should_exist": True
                }
            ]
        })

        return raw_value
