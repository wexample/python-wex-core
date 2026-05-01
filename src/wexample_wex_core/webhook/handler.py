from __future__ import annotations

import json
import logging
import subprocess
import time
import traceback
from http.server import BaseHTTPRequestHandler
from logging.handlers import RotatingFileHandler
from socketserver import TCPServer, ThreadingMixIn
from urllib.parse import urlparse

WEBHOOK_STATUS_STARTED = "started"
WEBHOOK_STATUS_COMPLETE = "complete"
WEBHOOK_STATUS_ERROR = "error"


class ThreadingHTTPServer(ThreadingMixIn, TCPServer):
    allow_reuse_address = True
    daemon_threads = True


class WebhookHttpRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for incoming webhook calls.

    Class-level attributes to set before serving:
        wex_executable : list[str]   — [python_path, main_py_path]
        log_path       : str         — absolute path to the rotating log file
        start_time     : float       — time.monotonic() at server startup
        type_resolvers : dict        — {command_type: WebhookTypeResolver}
    """

    log_path: str = ""
    start_time: float = 0.0
    type_resolvers: dict = {}
    wex_executable: list[str] = []

    # ------------------------------------------------------------------ GET
    def do_GET(self) -> None:
        import re

        from wexample_wex_core.webhook.const import WEBHOOK_ROUTES
        from wexample_wex_core.webhook.routing import (
            routing_build_command,
            routing_get_route_name,
            routing_is_allowed_route,
        )

        t0 = time.monotonic()
        output: dict = {}

        try:
            if not routing_is_allowed_route(self.path):
                self.send_response(404)
                self._send_json(
                    {"status": WEBHOOK_STATUS_ERROR, "error": "WEBHOOK_NOT_FOUND"}
                )
                return

            route_name = routing_get_route_name(self.path)
            assert route_name is not None

            # ---- /health (no auth required) ---------------------------------
            if route_name == "health":
                self.send_response(200)
                self._send_json(
                    {
                        "status": "ok",
                        "uptime_seconds": int(time.monotonic() - self.start_time),
                    }
                )
                return

            # ---- /webhook/{type}/{path} ------------------------------------
            route = WEBHOOK_ROUTES[route_name]
            parsed = urlparse(self.path)
            match = re.match(route["pattern"], parsed.path)
            assert match is not None

            command_type = match.group(1)
            command_path = match.group(2)

            # Resolve command string via resolver or generic routing
            resolver = type(self).type_resolvers.get(command_type)
            if resolver is not None:
                command_str = resolver.build_command(command_path)
            else:
                command_str = routing_build_command(command_type, command_path)

            if not command_str:
                self.send_response(400)
                self._send_json(
                    {"status": WEBHOOK_STATUS_ERROR, "error": "CANNOT_BUILD_COMMAND"}
                )
                return

            # ---- token validation ------------------------------------------
            if not self._validate_token(command_type, command_path, command_str):
                duration_ms = int((time.monotonic() - t0) * 1000)
                self._log_auth_failure(command_type, command_path)
                self.send_response(401)
                self._send_json(
                    {"status": WEBHOOK_STATUS_ERROR, "error": "UNAUTHORIZED"}
                )
                return

            # ---- dispatch --------------------------------------------------
            cwd = resolver.resolve_cwd(command_path) if resolver is not None else None

            cmd = self.wex_executable + [
                "core::webhook/exec",
                "--command-str",
                command_str,
                "--webhook-path",
                self.path,
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd,
            )

            duration_ms = int((time.monotonic() - t0) * 1000)

            from urllib.parse import parse_qs

            query_params = parse_qs(urlparse(self.path).query)
            is_async = route["is_async"] and query_params.get("_async", ["1"])[0] != "0"

            if not is_async:
                stdout, stderr = process.communicate()
                try:
                    response_data = json.loads(stdout) if stdout.strip() else {}
                except json.JSONDecodeError:
                    response_data = {"output": stdout}

                error = stderr[:500] if (stderr and process.returncode != 0) else None
                status = (
                    WEBHOOK_STATUS_COMPLETE
                    if process.returncode == 0
                    else WEBHOOK_STATUS_ERROR
                )
                output = {
                    "status": status,
                    "path": self.path,
                    "pid": process.pid,
                    "response": response_data,
                }
                if error:
                    output["error"] = error
            else:
                output = {
                    "status": WEBHOOK_STATUS_STARTED,
                    "path": self.path,
                    "pid": process.pid,
                }

            http_status = 200
            if not is_async and output.get("status") == WEBHOOK_STATUS_ERROR:
                http_status = 500
            self.send_response(http_status)
            self._log_request(
                command_type,
                command_path,
                output["status"],
                duration_ms,
                pid=process.pid,
            )

        except Exception as e:
            self.send_response(500)
            output = {
                "status": WEBHOOK_STATUS_ERROR,
                "error": str(e),
                "traceback": traceback.format_exc(),
            }
            self._get_logger().error(
                json.dumps({"error": str(e), "tb": traceback.format_exc()})
            )

        self._send_json(output)

    def log_message(self, format: str, *args: object) -> None:
        """Suppress the default stderr request logging."""

    # ------------------------------------------------------------------ auth
    def _extract_token(self) -> str | None:
        from urllib.parse import parse_qs

        auth = self.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            return auth[7:].strip() or None

        query = parse_qs(urlparse(self.path).query)
        tokens = query.get("_token", [])
        return tokens[0] if tokens else None

    def _validate_token(
        self, command_type: str, command_path: str, command_str: str
    ) -> bool:
        import hmac

        provided = self._extract_token()
        if not provided:
            return False

        resolver = type(self).type_resolvers.get(command_type)
        if resolver is None:
            return False

        expected = resolver.resolve_token(command_path, command_str)
        if not expected:
            return False

        return hmac.compare_digest(expected, provided)

    # ------------------------------------------------------------------ logging
    def _get_logger(self) -> logging.Logger:
        logger = logging.getLogger("wex-webhook")
        if not logger.handlers and self.log_path:
            handler = RotatingFileHandler(
                self.log_path, maxBytes=1_000_000, backupCount=5
            )
            handler.setFormatter(logging.Formatter("%(message)s"))
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _log_auth_failure(self, command_type: str, command_path: str) -> None:
        entry: dict = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "ip": self.client_address[0],
            "path": self.path,
            "command_type": command_type,
            "command_path": command_path,
            "status": "unauthorized",
        }
        self._get_logger().warning(json.dumps(entry))

    def _log_request(
        self,
        command_type: str,
        command_path: str,
        status: str,
        duration_ms: int,
        pid: int | None = None,
        error: str | None = None,
    ) -> None:
        entry: dict = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "ip": self.client_address[0],
            "path": self.path,
            "command_type": command_type,
            "command_path": command_path,
            "status": status,
            "duration_ms": duration_ms,
        }
        if pid is not None:
            entry["pid"] = pid
        if error:
            entry["error"] = error
        self._get_logger().info(json.dumps(entry))

    # ------------------------------------------------------------------ helpers
    def _send_json(self, data: dict) -> None:
        self.send_header("Content-type", "application/json")
        self.end_headers()
        try:
            self.wfile.write(json.dumps(data).encode())
        except BrokenPipeError:
            pass
