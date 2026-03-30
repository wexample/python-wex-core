from __future__ import annotations

import re


def yaml_substitute(text: str, variables: dict[str, str]) -> str:
    """Replace ``${VAR_NAME}`` placeholders with values from *variables*."""

    def _replace(match: re.Match) -> str:
        return variables.get(match.group(1), match.group(0))

    return re.sub(r"\$\{([^}]+)\}", _replace, text)


def yaml_substitute_step(step: dict, variables: dict[str, str]) -> dict:
    """Return a new step dict with all string values substituted.

    Applies recursively to nested dicts. Non-string values are passed through.
    """
    result = {}
    for key, value in step.items():
        if isinstance(value, str):
            result[key] = yaml_substitute(value, variables)
        elif isinstance(value, dict):
            result[key] = yaml_substitute_step(value, variables)
        else:
            result[key] = value
    return result
