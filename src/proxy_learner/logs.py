from __future__ import annotations

import re

from proxy_learner.domain import rule_key

FAILURE_KEYWORDS = (
    "timeout",
    "refused",
    "reset",
    "failed",
    "error",
    "unreachable",
)


def learned_targets(rule_lines: list[str]) -> set[str]:
    targets: set[str] = set()
    for line in rule_lines:
        _, target = rule_key(line)
        targets.add(target.lower())
    return targets


def find_failed_host(log_line: str, rule_lines: list[str]) -> str | None:
    lower = log_line.lower()
    if "direct" not in lower:
        return None
    if not any(keyword in lower for keyword in FAILURE_KEYWORDS):
        return None

    for target in learned_targets(rule_lines):
        if target in lower:
            return target

    host_match = re.search(
        r"(?:host|domain|server)=([a-z0-9][a-z0-9.-]*)",
        lower,
    )
    if host_match:
        candidate = host_match.group(1)
        if candidate in learned_targets(rule_lines):
            return candidate
    return None
