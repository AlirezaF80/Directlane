from __future__ import annotations

from pathlib import Path

import yaml

from proxy_learner.domain import rule_key


class RuleStore:
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    def list_rules(self) -> list[str]:
        if not self._path.exists():
            return []
        data = yaml.safe_load(self._path.read_text(encoding="utf-8")) or {}
        payload = data.get("payload", [])
        return [str(rule) for rule in payload]

    def add_rule(self, rule_line: str) -> bool:
        rule_key(rule_line)
        rules = self.list_rules()
        if rule_line in rules:
            return False
        rules.append(rule_line)
        self._write(rules)
        return True

    def remove_rule(self, rule_line: str) -> bool:
        rules = self.list_rules()
        if rule_line not in rules:
            return False
        rules.remove(rule_line)
        self._write(rules)
        return True

    def has_rule(self, rule_type: str, target: str) -> bool:
        candidate = f"{rule_type},{target},DIRECT"
        return candidate in self.list_rules()

    def _write(self, rules: list[str]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        content = {"payload": rules}
        self._path.write_text(
            yaml.safe_dump(content, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
