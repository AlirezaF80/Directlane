from __future__ import annotations

import os
from dataclasses import dataclass

from proxy_learner.karing_discovery import discover_karing


@dataclass(frozen=True)
class Config:
    karing_api_url: str
    karing_secret: str | None
    rules_path: str
    state_path: str
    rule_provider_name: str
    sighting_threshold: int
    poll_interval_seconds: float
    probe_attempts: int
    probe_required_successes: int
    probe_timeout_seconds: float

    @classmethod
    def from_env(cls) -> Config:
        discovered = discover_karing()
        default_api_url = discovered.api_url if discovered else "http://127.0.0.1:3057"
        default_secret = discovered.secret if discovered else None

        return cls(
            karing_api_url=os.environ.get(
                "KARING_API_URL", default_api_url
            ).rstrip("/"),
            karing_secret=os.environ.get("KARING_SECRET", default_secret) or None,
            rules_path=os.environ.get("RULES_PATH", "learned-direct.yaml"),
            state_path=os.environ.get("STATE_PATH", "state.json"),
            rule_provider_name=os.environ.get(
                "RULE_PROVIDER_NAME", "learned-direct"
            ),
            sighting_threshold=int(os.environ.get("SIGHTING_THRESHOLD", "3")),
            poll_interval_seconds=float(
                os.environ.get("POLL_INTERVAL_SECONDS", "5")
            ),
            probe_attempts=int(os.environ.get("PROBE_ATTEMPTS", "3")),
            probe_required_successes=int(
                os.environ.get("PROBE_REQUIRED_SUCCESSES", "2")
            ),
            probe_timeout_seconds=float(
                os.environ.get("PROBE_TIMEOUT_SECONDS", "5")
            ),
        )
