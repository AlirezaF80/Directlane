from __future__ import annotations

import ipaddress
import re

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


def to_rule_line(hostname: str) -> str:
    rule_type, target = to_rule_target(hostname)
    return f"{rule_type},{target},DIRECT"


def rule_key(rule_line: str) -> tuple[str, str]:
    match = re.match(r"^(DOMAIN(?:-SUFFIX|-KEYWORD)?|IP-CIDR),(.+),DIRECT$", rule_line)
    if not match:
        raise ValueError(f"invalid rule line: {rule_line}")
    return match.group(1), match.group(2)
