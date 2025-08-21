from typing import Any

from wexample_filestate_dev.workdir.mixins.with_version_workdir_mixin import WithVersionWorkdirMixin


class WithAppVersionWorkdirMixin(WithVersionWorkdirMixin):
    def _get_version_default_content(self) -> Any:
        from wexample_config.config_value.config_value import ConfigValue
        from wexample_wex_core.workdir.project_workdir import ProjectWorkdir

        class VersionBuilder(ConfigValue):
            workdir: ProjectWorkdir

            def get_str(self, type_check: bool = True) -> str:
                return self.workdir.get_config().get_config_item('version', default=self.raw).get_str()

        return VersionBuilder(
            raw=super()._get_version_default_content(),
            workdir=self
        )
