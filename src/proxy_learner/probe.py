from __future__ import annotations

import socket
import ssl
from collections.abc import Callable


def probe_tls(
    host: str,
    port: int = 443,
    timeout: float = 5.0,
    connect: Callable[..., socket.socket] | None = None,
) -> bool:
    try:
        context = ssl.create_default_context()
        opener = connect or socket.create_connection
        with opener((host, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=host):
                return True
    except OSError:
        return False


def confirm_outcome(
    host: str,
    *,
    expect_success: bool,
    attempts: int = 3,
    required: int = 2,
    probe: Callable[[str], bool] | None = None,
) -> bool:
    probe_fn = probe or probe_tls
    matches = sum(probe_fn(host) == expect_success for _ in range(attempts))
    return matches >= required


def confirm_probe(
    host: str,
    attempts: int = 3,
    required: int = 2,
    timeout: float = 5.0,
) -> bool:
    probe = lambda h: probe_tls(h, timeout=timeout)
    return confirm_outcome(host, expect_success=True, attempts=attempts, required=required, probe=probe)
