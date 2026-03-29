from __future__ import annotations

import psutil


def system_find_process_by_port(port: int) -> psutil.Process | None:
    """Return the first process listening on the given port, or None."""
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            for conn in proc.net_connections():
                if conn.laddr.port == port:
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return None
