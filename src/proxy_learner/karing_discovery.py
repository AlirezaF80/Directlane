from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class KaringDiscovery:
    api_url: str
    secret: str | None


def default_service_json_path() -> Path:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise FileNotFoundError("APPDATA is not set")
    return Path(appdata) / "karing" / "karing" / "service.json"


def discover_karing(service_json: Path | None = None) -> KaringDiscovery | None:
    path = service_json or default_service_json_path()
    if not path.exists():
        return None

    data = json.loads(path.read_text(encoding="utf-8"))
    port = data.get("control_port")
    if port is None:
        return None

    host = "127.0.0.1"
    secret = data.get("secret")
    return KaringDiscovery(
        api_url=f"http://{host}:{port}",
        secret=str(secret) if secret else None,
    )
