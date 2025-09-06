from wexample_filestate.config_value.content_config_value import ContentConfigValue
from wexample_wex_core.workdir.project_workdir import ProjectWorkdir

class VersionContentConfigValue(ContentConfigValue):
    workdir: ProjectWorkdir

    def build_content(self, type_check: bool = True) -> str:
        from wexample_helpers.helpers.string import string_ensure_end_with_new_line

        return string_ensure_end_with_new_line(
            self.workdir.get_config()
            .search(path="global.version", default=self.raw)
            .get_str()
        )