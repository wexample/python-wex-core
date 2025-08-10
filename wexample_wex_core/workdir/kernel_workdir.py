from typing import Optional, ClassVar

from wexample_config.const.types import DictConfig
from wexample_filestate.const.disk import DiskItemType
from wexample_wex_core.workdir.project_workdir import ProjectWorkdir


class KernelWorkdir(ProjectWorkdir):
    # Class-scoped constant for the tmp shortcut
    SHORTCUT_TMP: ClassVar[str] = "tmp"
    FILE_REGISTRY: ClassVar[str] = "registry.yml"

    def prepare_value(self, raw_value: Optional[DictConfig] = None) -> DictConfig:
        from wexample_wex_core.common.registry_builder import RegistryBuilder

        config = super().prepare_value(
            raw_value=raw_value
        )

        children = raw_value["children"]


        children.append({
            "shortcut": self.SHORTCUT_TMP,
            "name": self.SHORTCUT_TMP,
            "type": DiskItemType.DIRECTORY,
            "should_exist": True,
            "children": [
                {
                    "name": KernelWorkdir.FILE_REGISTRY,
                    "shortcut": "registry",
                    "default_content": RegistryBuilder()
                }
            ]
        })

        return config
