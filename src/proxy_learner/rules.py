from __future__ import annotations

import json
from pathlib import Path


class KaringRuleStore:
    def __init__(
        self,
        path: str | Path,
        *,
        group_name: str = "learned-direct",
    ) -> None:
        self._path = Path(path)
        self._group_name = group_name

    @property
    def path(self) -> Path:
        return self._path

    def list_domains(self) -> list[str]:
        return list(self._load_group().get("domain", []))

    def list_targets(self) -> set[str]:
        return {domain.lower() for domain in self.list_domains()}

    def has_rule(self, target: str) -> bool:
        return target.lower() in self.list_targets()

    def add_rule(self, target: str) -> bool:
        group = self._load_group()
        domain = target.lower()
        domains = group.setdefault("domain", [])
        if domain in domains:
            return False
        domains.append(domain)
        domains.sort()
        self._write_group(group)
        return True

    def remove_rule(self, target: str) -> bool:
        group = self._load_group()
        domain = target.lower()
        domains = group.get("domain", [])
        if domain not in domains:
            return False
        domains.remove(domain)
        self._write_group(group)
        return True

    def _empty_group(self) -> dict:
        return {
            "outbound": "direct",
            "name": self._group_name,
            "switch": True,
            "or": True,
        }

    def _load_group(self) -> dict:
        if not self._path.exists():
            return self._empty_group()
        data = json.loads(self._path.read_text(encoding="utf-8"))
        rules = data.get("rules", [])
        if not rules:
            return self._empty_group()
        group = dict(rules[0])
        group.pop("domain_suffix", None)
        return group

    def _write_group(self, group: dict) -> None:
        group.pop("domain_suffix", None)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        document = {"rules": [group]}
        self._path.write_text(
            json.dumps(document, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
