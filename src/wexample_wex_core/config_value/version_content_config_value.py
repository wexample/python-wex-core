from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate.config_value.content_config_value import ContentConfigValue
from wexample_helpers.decorator.base_class import base_class
from wexample_wex_core.workdir.project_workdir import ProjectWorkdir

if TYPE_CHECKING:
    from wexample_wex_core.workdir.project_workdir import ProjectWorkdir


@base_class
class VersionContentConfigValue(ContentConfigValue):
    workdir: ProjectWorkdir

    def build_content(self, type_check: bool = True) -> str:
        from wexample_helpers.helpers.string import string_ensure_end_with_new_line

        return string_ensure_end_with_new_line(
            self.workdir.get_config()
            .search(path="global.version", default=self.raw)
            .get_str()
        )
