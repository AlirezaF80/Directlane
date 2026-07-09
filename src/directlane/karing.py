from __future__ import annotations

from typing import Any

import requests

from directlane.domain import normalize_host


class KaringClient:
    def __init__(
        self,
        base_url: str,
        secret: str | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._session = session or requests.Session()
        if secret:
            self._session.headers["Authorization"] = f"Bearer {secret}"

    def get_connections(self) -> list[dict[str, Any]]:
        response = self._session.get(
            f"{self._base_url}/connections",
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
        return list(payload.get("connections", []))

    def reload_rule_provider(self, provider_name: str) -> bool:
        response = self._session.put(
            f"{self._base_url}/providers/rules/{provider_name}",
            timeout=10,
        )
        if response.status_code == 404:
            return False
        response.raise_for_status()
        return True

    def iter_log_lines(self, level: str = "warning") -> requests.Response:
        return self._session.get(
            f"{self._base_url}/logs",
            params={"level": level},
            stream=True,
            timeout=10,
        )


def extract_host(connection: dict[str, Any]) -> str | None:
    metadata = connection.get("metadata") or {}
    host = metadata.get("host")
    if not host:
        return None
    return normalize_host(str(host))


def is_proxied_connection(connection: dict[str, Any]) -> bool:
    chains = connection.get("chains") or []
    if not chains:
        return False
    last_hop = str(chains[-1]).upper()
    return last_hop not in {"DIRECT", "REJECT"}


def is_learned_direct_connection(connection: dict[str, Any]) -> bool:
    rule = str(connection.get("rule", ""))
    rule_payload = str(connection.get("rulePayload", ""))
    chains = [str(item).upper() for item in connection.get("chains") or []]
    if "DIRECT" not in chains:
        return False
    return "LEARNED-DIRECT" in rule.upper() or "learned-direct" in rule_payload.lower()
