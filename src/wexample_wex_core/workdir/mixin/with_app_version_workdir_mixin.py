from __future__ import annotations

from typing import Any

from wexample_filestate.workdir.mixin.with_version_workdir_mixin import (
    WithVersionWorkdirMixin,
)


class WithAppVersionWorkdirMixin(WithVersionWorkdirMixin):
    def _get_version_default_content(self) -> Any:
        from wexample_config.config_value.config_value import ConfigValue
        from wexample_config.options_provider.abstract_options_provider import (
            AbstractOptionsProvider,
        )
        from wexample_filestate.const.state_items import SourceFileOrDirectory
        from wexample_filestate.operations_provider.abstract_operations_provider import (
            AbstractOperationsProvider,
        )
        from wexample_filestate.result.abstract_result import AbstractResult
        from wexample_helpers.helpers.polyfill import polyfill_import
        from wexample_wex_core.config_value.version_content_config_value import (
            VersionContentConfigValue,
        )

        polyfill_import(
            ConfigValue,
            AbstractOptionsProvider,
            SourceFileOrDirectory,
            AbstractOperationsProvider,
            AbstractResult,
        )
        VersionContentConfigValue.model_rebuild()

        return VersionContentConfigValue(
            raw=super()._get_version_default_content(), workdir=self
        )
