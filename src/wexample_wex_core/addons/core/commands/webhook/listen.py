from __future__ import annotations

import subprocess
import sys
import time
from typing import TYPE_CHECKING

from wexample_cli.decorator.command import command
from wexample_cli.decorator.option import option
from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_wex_core.addons.core.const.tags import DomainTag

from wexample_wex_core.const.globals import COMMAND_TYPE_ADDON
from wexample_wex_core.webhook.const import WEBHOOK_LISTEN_PORT_DEFAULT

if TYPE_CHECKING:
    from wexample_app.response.abstract_response import AbstractResponse
    from wexample_cli.context.execution_context import ExecutionContext


@option(
    "port",
    type=int,
    short_name="p",
    required=False,
    default=WEBHOOK_LISTEN_PORT_DEFAULT,
    description="Port to listen on",
)
@option(
    "asynchronous",
    type=bool,
    short_name="a",
    is_flag=True,
    required=False,
    default=False,
    description="Run as a background subprocess",
)
@option(
    "force",
    type=bool,
    short_name="f",
    is_flag=True,
    required=False,
    default=False,
    description="Kill any existing process on the port before starting",
)
@option(
    "dry_run",
    type=bool,
    short_name="d",
    is_flag=True,
    required=False,
    default=False,
    description="Bind the socket without serving (useful for tests)",
)
@option(
    "worker_timeout",
    type=int,
    required=False,
    default=300,
    description="Subprocess timeout in seconds for synchronous calls (0 = no limit)",
)
@command(type=COMMAND_TYPE_ADDON, description="Start the webhook HTTP daemon",
    tags=[
        DomainTag.CORE,
        DomainTag.HTTP,
        DomainTag.WEBHOOK,
        EffectTag.LONG_RUNNING,
        EffectTag.SUBPROCESS_SPAWN,
        AudienceTag.AGENT_SAFE,
        ScopeTag.GLOBAL,
        ScopeTag.LOCAL,
    ],
)
def core__webhook__listen(
    context: ExecutionContext,
    port: int = WEBHOOK_LISTEN_PORT_DEFAULT,
    asynchronous: bool = False,
    force: bool = False,
    dry_run: bool = False,
    worker_timeout: int = 300,
) -> AbstractResponse | None:
    import psutil

    from wexample_wex_core.addons.system.helpers import system_find_process_by_port

    # ---- port conflict check -------------------------------------------------
    existing = system_find_process_by_port(port)
    if existing:
        if force:
            context.io.log(f"Port {port} in use (pid {existing.pid}), terminating...")
            try:
                existing.terminate()
                existing.wait(timeout=5)
            except psutil.TimeoutExpired:
                existing.kill()
            time.sleep(0.5)
        else:
            from wexample_app.response.failure_response import FailureResponse

            return FailureResponse(
                kernel=context.kernel,
                message=f"Port {port} already in use by pid {existing.pid}. Use --force to kill it.",
            )

    # ---- async mode: spawn self as background subprocess --------------------
    if asynchronous:
        cmd = [
            sys.executable,
            sys.argv[0],
            "core::webhook/listen",
            "--port",
            str(port),
        ]
        process = subprocess.Popen(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        from wexample_wex_core.addons.system.helpers import (
            system_find_process_by_port as _chk,
        )

        running = None
        for _ in range(10):
            time.sleep(0.5)
            running = _chk(port)
            if running:
                break

        from wexample_app.response.failure_response import FailureResponse
        from wexample_app.response.success_response import SuccessResponse

        if running:
            return SuccessResponse(
                kernel=context.kernel,
                message=f"Webhook daemon started on port {port} (pid {process.pid})",
            )
        return FailureResponse(
            kernel=context.kernel,
            message=f"Daemon spawned (pid {process.pid}) but port {port} is not bound yet",
        )

    # ---- sync mode: serve in this process (blocking) -----------------------
    from wexample_wex_core.webhook.handler import (
        ThreadingHTTPServer,
        WebhookHttpRequestHandler,
    )

    log_path = _resolve_log_path(context)

    class _Handler(WebhookHttpRequestHandler):
        wex_executable = [sys.executable, sys.argv[0]]
        start_time = time.monotonic()

    _Handler.log_path = log_path
    _Handler.worker_timeout = worker_timeout
    _Handler.type_resolvers = _load_type_resolvers(context.kernel)

    context.io.log(f"Starting webhook daemon on port {port}  |  log: {log_path}")

    if not dry_run:
        with ThreadingHTTPServer(("", port), _Handler) as server:
            _install_sigterm_handler(server)
            server.serve_forever()

    return None


def _install_sigterm_handler(server: object) -> None:
    import signal
    import threading

    def _handler(signum: int, frame: object) -> None:
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, _handler)


def _load_type_resolvers(kernel) -> Registry:
    from wexample_helpers.service.registry import Registry

    from wexample_wex_core.webhook.addon_resolver import AddonWebhookTypeResolver
    from wexample_wex_core.webhook.resolver import WebhookTypeResolver
    from wexample_wex_core.webhook.service_resolver import ServiceWebhookTypeResolver

    workdir_path = str(kernel.workdir.get_path())
    registry: Registry[WebhookTypeResolver] = Registry()
    registry.register(AddonWebhookTypeResolver(workdir_path), key="addon")
    registry.register(ServiceWebhookTypeResolver(workdir_path), key="service")

    for addon in kernel.get_addons().values():
        for key, resolver in addon.get_webhook_resolvers().items():
            registry.register(resolver, key=key)

    return registry


def _resolve_log_path(context: ExecutionContext) -> str:
    from pathlib import Path

    log_dir = Path(context.kernel.workdir.get_path()) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return str(log_dir / "webhook.log")
