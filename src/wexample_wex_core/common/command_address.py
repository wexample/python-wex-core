from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CommandAddress:
    """Structured identity of an addon command.

    Holds the three canonical components (addon, group, name) and converts
    between every representation used in the system: command string, function
    name, file path, test path.
    """

    addon: str
    group: str
    name: str

    # ------------------------------------------------------------------
    # Factories
    # ------------------------------------------------------------------

    @classmethod
    def from_function(cls, function) -> CommandAddress:
        """Build from a command function or CommandMethodWrapper, e.g. ``default__ping__pong``."""
        from wexample_wex_core.common.command_method_wrapper import CommandMethodWrapper

        if isinstance(function, CommandMethodWrapper):
            return cls.from_function_name(function.function.__name__)
        return cls.from_function_name(function.__name__)

    @classmethod
    def from_function_name(cls, function_name: str) -> CommandAddress:
        """Build from a Python function name, e.g. ``default__registry__build``."""
        from wexample_wex_core.const.globals import COMMAND_SEPARATOR_FUNCTION_PARTS

        parts = function_name.split(COMMAND_SEPARATOR_FUNCTION_PARTS, 2)
        return cls(addon=parts[0], group=parts[1], name=parts[2])

    @classmethod
    def from_path(
        cls, path: Path, addon_name: str, commands_base: Path
    ) -> CommandAddress:
        """Build from a command file path.

        ``commands_base`` is the ``commands/`` directory of the addon.
        The addon name must be provided separately as it is not encoded in the path.
        """
        relative = path.relative_to(commands_base)
        return cls(addon=addon_name, group=relative.parts[0], name=relative.stem)

    # ------------------------------------------------------------------
    # Conversions
    # ------------------------------------------------------------------

    def to_command_key(self) -> str:
        """Return the within-addon key, e.g. ``registry/build``."""
        from wexample_wex_core.const.globals import COMMAND_SEPARATOR_GROUP

        return f"{self.group}{COMMAND_SEPARATOR_GROUP}{self.name}"

    def to_function_name(self) -> str:
        """Return the Python function name, e.g. ``default__registry__build``."""
        from wexample_wex_core.const.globals import COMMAND_SEPARATOR_FUNCTION_PARTS

        return COMMAND_SEPARATOR_FUNCTION_PARTS.join([self.addon, self.group, self.name])

    def to_relative_path(self, extension: str = "py") -> Path:
        """Return the path relative to a ``commands/`` or ``tests/`` base dir."""
        return Path(self.group) / f"{self.name}.{extension}"
