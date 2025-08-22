from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_config.const.types import DictConfig
from wexample_filestate.const.disk import DiskItemType
from wexample_filestate_dev.workdir.mixins.with_readme_workdir_mixin import (
    WithReadmeWorkdirMixin,
)
from wexample_wex_addon_app.const.globals import (
    APP_DIR_APP_DATA_NAME,
    APP_FILE_APP_CONFIG,
    APP_FILE_APP_ENV,
)
from wexample_wex_core.workdir.mixin.with_app_version_workdir_mixin import (
    WithAppVersionWorkdirMixin,
)
from wexample_wex_core.workdir.workdir import Workdir

if TYPE_CHECKING:
    from wexample_config.config_value.nested_config_value import NestedConfigValue


class ProjectWorkdir(WithReadmeWorkdirMixin, WithAppVersionWorkdirMixin, Workdir):

    @classmethod
    def create_from_config(cls, **kwargs) -> ProjectWorkdir:

        from wexample_filestate.config_option.class_config_option import (
            ClassConfigOption,
        )
        from wexample_helpers.helpers.module import module_are_same

        config = kwargs.get("config")

        instance = super().create_from_config(**kwargs)

        if isinstance(config, dict):
            ClassConfigOption.get_snake_short_class_name()
            preferred = instance.get_preferred_workdir_class()
            if preferred:
                # The loaded class definition is a different one.
                if not module_are_same(preferred, cls):
                    return preferred.create_from_config(**kwargs)
        return instance

    def get_config(self) -> NestedConfigValue:
        from wexample_config.config_value.nested_config_value import NestedConfigValue

        config_yml = self.find_by_name_recursive(item_name=APP_FILE_APP_CONFIG)
        if config_yml:
            return config_yml.read_as_config()

        return NestedConfigValue()

    def get_preferred_workdir_class(self) -> type[ProjectWorkdir] | None:
        from wexample_helpers.helpers.module import module_load_class_from_file

        path = self.get_path()
        manager_config = self.get_config().search("files_state.manager")

        if manager_config:
            file_relative = manager_config.get_config_item("file").get_str()
            class_name = manager_config.get_config_item("class").get_str()

            # Compute absolute path to the python file
            file_abs_path = path / file_relative

            if file_abs_path.exists():
                # Dynamically load the module and fetch the class
                class_module = module_load_class_from_file(
                    file_path=file_abs_path,
                    class_name=class_name,
                )

                # Good format
                if issubclass(class_module, ProjectWorkdir):
                    return class_module
                else:
                    self.io.warning(
                        f"Custom class '{class_name}' defined in {APP_FILE_APP_CONFIG} was found at {file_abs_path}, "
                        f"but it must be a subclass of {ProjectWorkdir.__name__}."
                    )
            else:
                self.io.warning(
                    f"Custom manager file '{file_relative}' configured in {APP_FILE_APP_CONFIG} "
                    f"does not exist at {file_abs_path}."
                )
        return None

    def prepare_value(self, raw_value: DictConfig | None = None) -> DictConfig:
        from wexample_filestate.config_option.text_filter_config_option import (
            TextFilterConfigOption,
        )
        from wexample_filestate.item.file.yaml_file import YamlFile

        raw_value = super().prepare_value(raw_value)

        raw_value.update(
            {
                "mode": "777",
                "mode_recursive": True,
            }
        )

        children = raw_value["children"]

        self.append_readme(config=raw_value)
        self.append_version(config=raw_value)

        children.append(
            {
                "name": ".gitignore",
                "type": DiskItemType.FILE,
                "should_exist": True,
                "text_filter": [TextFilterConfigOption.OPTION_NAME_ENSURE_NEWLINE],
            }
        )

        children.append(
            {
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
                        "yaml_filter": ["sort_recursive"],
                    },
                    {
                        # tmp
                        "name": "tmp",
                        "type": DiskItemType.DIRECTORY,
                        "should_exist": True,
                    },
                ],
            }
        )

        return raw_value
