from __future__ import annotations

from typing import Any

from wexample_filestate.workdir.mixin.with_version_workdir_mixin import (
    WithVersionWorkdirMixin,
)


class WithAppVersionWorkdirMixin(WithVersionWorkdirMixin):
    def _get_version_default_content(self) -> Any:
        from wexample_wex_core.config_value.version_content_config_value import VersionContentConfigValue

        return VersionContentConfigValue(
            raw=super()._get_version_default_content(),
            workdir=self
        )
