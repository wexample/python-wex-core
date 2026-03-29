from __future__ import annotations

import re


def yaml_substitute(text: str, variables: dict[str, str]) -> str:
    """Replace ``${VAR_NAME}`` placeholders with values from *variables*."""

    def _replace(match: re.Match) -> str:
        return variables.get(match.group(1), match.group(0))

    return re.sub(r"\$\{([^}]+)\}", _replace, text)
