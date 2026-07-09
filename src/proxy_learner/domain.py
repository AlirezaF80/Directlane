from __future__ import annotations

import ipaddress

STRIP_LABELS = frozenset({"www", "cdn", "api", "static", "m", "mobile"})


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
    if is_ip_address(host):
        return ("DOMAIN", host)

    labels = host.split(".")
    if len(labels) < 2:
        return ("DOMAIN", host)

    if labels[0] in STRIP_LABELS and len(labels) >= 3:
        base = ".".join(labels[1:])
    elif len(labels) == 2:
        base = host
    else:
        base = ".".join(labels[-2:])

    if "." not in base:
        return ("DOMAIN", host)
    return ("DOMAIN-SUFFIX", base)
