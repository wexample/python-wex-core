from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse


def routing_get_route_name(path: str) -> str | None:
    """Match a request path against known webhook routes and return the route name."""
    from wexample_wex_core.webhook.const import WEBHOOK_ROUTES

    parsed_path = urlparse(path).path
    for route_name, route in WEBHOOK_ROUTES.items():
        if re.match(route["pattern"], parsed_path):
            return route_name
    return None


def routing_is_allowed_route(path: str) -> bool:
    """Return True if the path matches a known route and all query params are safe."""
    from wexample_wex_core.webhook.const import ALLOWED_QUERY_NAME, ALLOWED_QUERY_VALUE

    if not routing_get_route_name(path):
        return False

    parsed = urlparse(path)
    query = parse_qs(parsed.query)
    for key, values in query.items():
        if not ALLOWED_QUERY_NAME.fullmatch(key):
            return False
        for value in values:
            if not ALLOWED_QUERY_VALUE.fullmatch(value):
                return False

    return True


def routing_build_command(command_type: str, command_path: str) -> str | None:
    """Convert URL components to a wex command string.

    Examples:
        addon / app/info/show   →  app::info/show
        app   / remote/push     →  .remote/push
        service / nginx/status  →  @nginx::status
    """
    if command_type == "addon":
        parts = command_path.split("/")
        if len(parts) < 2:
            return None
        addon = parts[0]
        rest = "/".join(parts[1:])
        return f"{addon}::{rest}"

    if command_type == "app":
        return f".{command_path}"

    if command_type == "service":
        parts = command_path.split("/")
        if len(parts) < 2:
            return None
        service = parts[0]
        rest = "/".join(parts[1:])
        return f"@{service}::{rest}"

    return None
