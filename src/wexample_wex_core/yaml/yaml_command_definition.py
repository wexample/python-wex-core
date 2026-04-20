from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from wexample_app.command.option import Option


class YamlCommandDefinition:
    """Immutable parsed representation of a YAML command file.

    Parsed once per file path; callers should cache instances.
    """

    def __init__(self, path: Path, data: dict) -> None:
        self.path = path
        self.description: str | None = data.get("description")
        self.scripts: list[dict] = data.get("scripts", [])
        self.options: list[Option] = self._parse_options(data.get("options", []))
        aliases, sudo, webhook, attachments = self._parse_decorators(
            data.get("decorators", [])
        )
        self.aliases: list[str] = aliases
        self.sudo: bool = sudo
        self.webhook: bool = webhook
        self.attachments: dict[str, list] = attachments

    @classmethod
    def from_path(cls, path: Path) -> YamlCommandDefinition:
        import yaml

        with open(path) as f:
            data = yaml.safe_load(f) or {}
        return cls(path=path, data=data)

    def _parse_decorators(
        self, decorators: list
    ) -> tuple[list[str], bool, bool, dict[str, list]]:
        aliases: list[str] = []
        sudo = False
        webhook = False
        attachments: dict[str, list] = {"before": [], "after": [], "always_after": []}

        for dec in decorators:
            name = dec.get("name")
            args: Any = dec.get("args", {})

            if name == "sudo":
                sudo = True
            elif name == "webhook":
                webhook = True
            elif name == "alias":
                aliases.append(args if isinstance(args, str) else str(args))
            elif name == "attach" and isinstance(args, dict):
                position = args.get("position", "after")
                attachments.setdefault(position, []).append(
                    {
                        "command": args.get("command", ""),
                        "pass_args": args.get("pass_args", False),
                    }
                )

        return aliases, sudo, webhook, attachments

    # ------------------------------------------------------------------
    # Parsing helpers
    # ------------------------------------------------------------------
    def _parse_options(self, options_data: list) -> list[Option]:
        from wexample_app.command.option import Option

        _type_map: dict[str, type] = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
        }
        options = []

        for opt in options_data:
            name = opt.get("name")
            if not name:
                continue

            python_type = _type_map.get(opt.get("type", "str"), str)
            options.append(
                Option(
                    name=name,
                    type=python_type,
                    required=opt.get("required", False),
                    default=opt.get("default"),
                    description=opt.get("help"),
                    short_name=opt.get("short"),
                    is_flag=opt.get("is_flag", False),
                    multiple=opt.get("multiple", False),
                )
            )

        return options
