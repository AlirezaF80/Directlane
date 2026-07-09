from __future__ import annotations

import json
from pathlib import Path


class LearnerState:
    def __init__(
        self,
        path: str | Path,
        sighting_threshold: int = 3,
    ) -> None:
        self._path = Path(path)
        self._sighting_threshold = sighting_threshold
        self._sightings: dict[str, int] = {}
        self._load()

    def record_sighting(self, host: str) -> int:
        host = host.lower()
        self._sightings[host] = self._sightings.get(host, 0) + 1
        self._save()
        return self._sightings[host]

    def get_sighting_count(self, host: str) -> int:
        return self._sightings.get(host.lower(), 0)

    def is_ready_for_probe(self, host: str) -> bool:
        return self.get_sighting_count(host) >= self._sighting_threshold

    def mark_probed(self, host: str) -> None:
        self._sightings[host.lower()] = 0
        self._save()

    def _load(self) -> None:
        if not self._path.exists():
            return
        data = json.loads(self._path.read_text(encoding="utf-8"))
        self._sightings = {
            str(host): int(count) for host, count in data.get("sightings", {}).items()
        }

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"sightings": self._sightings}
        self._path.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )
