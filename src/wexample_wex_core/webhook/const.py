from __future__ import annotations

import re

# filestate: python-constant-sort
WEBHOOK_LISTEN_PORT_DEFAULT: int = 6543

WEBHOOK_ROUTES: dict = {
    "exec": {
        "is_async": True,
        "pattern": r"^/webhook/(addon|app|service)/(.+)$",
    },
    "health": {
        "is_async": False,
        "pattern": r"^/health$",
    },
    "metrics": {
        "is_async": False,
        "pattern": r"^/metrics$",
    },
}

# Allowed characters in query parameter names and values.
# Values allow path-like chars (/ .) so app_path can be passed as query param.
ALLOWED_QUERY_NAME: re.Pattern = re.compile(r"^[a-zA-Z0-9_]+$")
ALLOWED_QUERY_VALUE: re.Pattern = re.compile(r"^[a-zA-Z0-9_.+\-\/]+$")
