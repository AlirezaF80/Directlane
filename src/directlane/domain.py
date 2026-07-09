from __future__ import annotations

import ipaddress


def normalize_host(hostname: str) -> str:
    host = hostname.lower().strip().rstrip(".")
    return host


def is_ip_address(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def to_rule_target(hostname: str) -> tuple[str, str]:
    host = normalize_host(hostname)
    if not host:
        raise ValueError("hostname must not be empty")
    return ("DOMAIN", host)
