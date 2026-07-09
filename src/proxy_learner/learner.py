from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from proxy_learner.domain import to_rule_target
from proxy_learner.probe import confirm_outcome
from proxy_learner.rules import KaringRuleStore
from proxy_learner.state import ProbeState


class Learner:
    def __init__(
        self,
        rules_path: str | Path,
        state_path: str | Path,
        probe: Callable[[str], bool] | None = None,
        on_rules_changed: Callable[[], None] | None = None,
        probe_attempts: int = 3,
        probe_required_successes: int = 2,
        probe_timeout_seconds: float = 5.0,
        group_name: str = "learned-direct",
    ) -> None:
        self.rules = KaringRuleStore(rules_path, group_name=group_name)
        self.state = ProbeState(state_path)
        self._probe = probe
        self._on_rules_changed = on_rules_changed
        self._probe_attempts = probe_attempts
        self._probe_required_successes = probe_required_successes
        self._probe_timeout_seconds = probe_timeout_seconds
        self._seen_connection_ids: set[str] = set()

    def handle_proxied_host(self, host: str) -> bool:
        host = host.lower()
        _, target = to_rule_target(host)
        if self.rules.has_rule(target):
            return False
        if self.state.was_probed(target):
            return False

        if not self._run_probe(host):
            self.state.mark_probed(target)
            return False

        added = self.rules.add_rule(target)
        self.state.mark_probed(target)
        if added and self._on_rules_changed is not None:
            self._on_rules_changed()
        return added

    def handle_direct_failure(
        self,
        host: str,
        probe: Callable[[str], bool] | None = None,
    ) -> bool:
        host = host.lower()
        _, target = to_rule_target(host)
        if not self.rules.has_rule(target):
            return False

        if not self._confirm_direct_failure(host, probe=probe):
            return False

        removed = self.rules.remove_rule(target)
        if removed:
            self.state.clear(target)
            if self._on_rules_changed is not None:
                self._on_rules_changed()
        return removed

    def process_connections(self, connections: list[dict]) -> None:
        for connection in connections:
            connection_id = str(connection.get("id", ""))
            if connection_id:
                if connection_id in self._seen_connection_ids:
                    continue
                self._seen_connection_ids.add(connection_id)
                if len(self._seen_connection_ids) > 10_000:
                    self._seen_connection_ids.clear()

            from proxy_learner.karing import (
                extract_host,
                is_proxied_connection,
            )

            host = extract_host(connection)
            if not host:
                continue
            if is_proxied_connection(connection):
                self.handle_proxied_host(host)

    def _run_probe(self, host: str) -> bool:
        return confirm_outcome(
            host,
            expect_success=True,
            attempts=self._probe_attempts,
            required=self._probe_required_successes,
            probe=self._default_probe,
        )

    def _confirm_direct_failure(
        self,
        host: str,
        probe: Callable[[str], bool] | None = None,
    ) -> bool:
        probe_fn = probe or self._default_probe
        return confirm_outcome(
            host,
            expect_success=False,
            attempts=self._probe_attempts,
            required=self._probe_required_successes,
            probe=probe_fn,
        )

    def _default_probe(self, host: str) -> bool:
        if self._probe is not None:
            return self._probe(host)
        return probe_tls_with_timeout(host, self._probe_timeout_seconds)


def probe_tls_with_timeout(host: str, timeout: float) -> bool:
    from proxy_learner.probe import probe_tls

    return probe_tls(host, timeout=timeout)
