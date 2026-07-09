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

    def list_domain_suffixes(self) -> list[str]:
        return list(self._load_group().get("domain_suffix", []))

    def list_domains(self) -> list[str]:
        return list(self._load_group().get("domain", []))

    def list_targets(self) -> set[str]:
        targets = {suffix.lstrip(".").lower() for suffix in self.list_domain_suffixes()}
        targets.update(domain.lower() for domain in self.list_domains())
        return targets

    def has_rule(self, rule_type: str, target: str) -> bool:
        target = target.lower()
        if rule_type == "DOMAIN-SUFFIX":
            return f".{target}" in [s.lower() for s in self.list_domain_suffixes()]
        if rule_type == "DOMAIN":
            return target in [d.lower() for d in self.list_domains()]
        return False

    def add_rule(self, rule_type: str, target: str) -> bool:
        group = self._load_group()
        if rule_type == "DOMAIN-SUFFIX":
            suffix = f".{target.lower().lstrip('.')}"
            suffixes = group.setdefault("domain_suffix", [])
            if suffix in suffixes:
                return False
            suffixes.append(suffix)
            suffixes.sort()
        elif rule_type == "DOMAIN":
            domain = target.lower()
            domains = group.setdefault("domain", [])
            if domain in domains:
                return False
            domains.append(domain)
            domains.sort()
        else:
            raise ValueError(f"unsupported rule type: {rule_type}")
        self._write_group(group)
        return True

    def remove_rule(self, rule_type: str, target: str) -> bool:
        group = self._load_group()
        if rule_type == "DOMAIN-SUFFIX":
            suffix = f".{target.lower().lstrip('.')}"
            suffixes = group.get("domain_suffix", [])
            if suffix not in suffixes:
                return False
            suffixes.remove(suffix)
        elif rule_type == "DOMAIN":
            domain = target.lower()
            domains = group.get("domain", [])
            if domain not in domains:
                return False
            domains.remove(domain)
        else:
            raise ValueError(f"unsupported rule type: {rule_type}")
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
        return dict(rules[0])

    def _write_group(self, group: dict) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        document = {"rules": [group]}
        self._path.write_text(
            json.dumps(document, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
