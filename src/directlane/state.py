from __future__ import annotations

import json
from pathlib import Path


class ProbeState:
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._probed_hosts: set[str] = set()
        self._load()

    def was_probed(self, host: str) -> bool:
        return host.lower() in self._probed_hosts

    def mark_probed(self, host: str) -> None:
        self._probed_hosts.add(host.lower())
        self._save()

    def clear(self, host: str) -> None:
        self._probed_hosts.discard(host.lower())
        self._save()

    def _load(self) -> None:
        if not self._path.exists():
            return
        data = json.loads(self._path.read_text(encoding="utf-8"))
        self._probed_hosts = {str(host).lower() for host in data.get("probed_hosts", [])}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"probed_hosts": sorted(self._probed_hosts)}
        self._path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
