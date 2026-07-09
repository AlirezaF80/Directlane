from __future__ import annotations

import re

FAILURE_KEYWORDS = (
    "timeout",
    "refused",
    "reset",
    "failed",
    "error",
    "unreachable",
)


def find_failed_host(log_line: str, targets: set[str]) -> str | None:
    lower = log_line.lower()
    if "direct" not in lower:
        return None
    if not any(keyword in lower for keyword in FAILURE_KEYWORDS):
        return None

    for target in targets:
        if target in lower:
            return target

    host_match = re.search(
        r"(?:host|domain|server)=([a-z0-9][a-z0-9.-]*)",
        lower,
    )
    if host_match:
        candidate = host_match.group(1)
        if candidate in targets:
            return candidate
    return None
