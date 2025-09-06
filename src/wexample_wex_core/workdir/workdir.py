from __future__ import annotations
from wexample_filestate.file_state_manager import FileStateManager
from wexample_helpers.const.types import StringKeysDict
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from wexample_config.const.types import DictConfig


class Workdir(FileStateManager):
    _child_setup_dir: StringKeysDict | None = None

    def prepare_value(self, raw_value: DictConfig | None = None) -> DictConfig:
        from wexample_app.const.globals import APP_FILE_APP_CONFIG
        from wexample_filestate.config_value.aggregated_templates_config_value import AggregatedTemplatesConfigValue
        from wexample_filestate.const.disk import DiskItemType
        from wexample_filestate.item.file.env_file import EnvFile
        from wexample_filestate.config_option.text_filter_config_option import TextFilterConfigOption
        from wexample_wex_core.const.globals import WORKDIR_SETUP_DIR
        from wexample_filestate.item.file.yaml_file import YamlFile

        raw_value = super().prepare_value(raw_value)

        if "children" not in raw_value:
            raw_value["children"] = []

        self._child_setup_dir = {
            # .wex
            "name": WORKDIR_SETUP_DIR,
            "type": DiskItemType.DIRECTORY,
            "should_exist": True,
            "children": [
                {
                    # .env
                    "class": EnvFile,
                    "name": EnvFile.EXTENSION_DOT_ENV,
                    "type": DiskItemType.FILE,
                    "should_exist": True,
                    "text_filter": [TextFilterConfigOption.OPTION_NAME_ENSURE_NEWLINE],
                },
                {
                    # config.yml
                    "name": APP_FILE_APP_CONFIG,
                    "type": DiskItemType.FILE,
                    "should_exist": True,
                    "class": YamlFile,
                    "text_filter": [
                        TextFilterConfigOption.OPTION_NAME_ENSURE_NEWLINE,
                        "tmp/",
                    ],
                    "yaml_filter": ["sort_recursive"],
                },
                {
                    # python (app manager)
                    "name": "bin",
                    "type": DiskItemType.DIRECTORY,
                    "should_exist": True,
                    "children": [
                        {
                            "name": "app-manager",
                            "type": DiskItemType.FILE,
                            "should_exist": True,
                            "content": AggregatedTemplatesConfigValue(
                                templates=[
                                    "#!/usr/bin/env bash",
                                    "set -euo pipefail",
                                    'ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"',
                                    'APP_ROOT="${APP_ROOT:-$ROOT}"',
                                    'AM_DIR="$ROOT/.wex/python/app_manager"',
                                    'VENV="$AM_DIR/.venv"',
                                    'PY="$VENV/bin/python3"',
                                    "",
                                    'if [ ! -x "$PY" ]; then',
                                    '  python3 -m venv "$VENV"',
                                    '  "$PY" -m pip install -U pip wheel',
                                    "fi",
                                    "",
                                    "# Prefer local core in editable mode if available; fallback to PyPI dep",
                                    'CORE_DIR="$ROOT/../../wex-core"',
                                    'if [ -d "$CORE_DIR" ]; then',
                                    '  "$PY" -m pip install -e "$CORE_DIR"',
                                    "else",
                                    "  # Ensure core from PyPI is present (respect pyproject if you later switch to PDM)",
                                    '  "$PY" -m pip install -U wexample-wex-core',
                                    "fi",
                                    "",
                                    "export APP_ROOT",
                                    'exec "$PY" -m wexample_wex_core.app_manager -- "$@"',
                                ]
                            ),
                        }
                    ],
                },
                {
                    # tmp
                    "name": "tmp",
                    "type": DiskItemType.DIRECTORY,
                    "should_exist": True,
                },
                {
                    "name": ".gitignore",
                    "type": DiskItemType.FILE,
                    "should_exist": True,
                    "should_contain_lines": [EnvFile.EXTENSION_DOT_ENV],
                    "text_filter": [TextFilterConfigOption.OPTION_NAME_ENSURE_NEWLINE],
                },
            ],
        }

        raw_value["children"].append(self._child_setup_dir)

        return raw_value
