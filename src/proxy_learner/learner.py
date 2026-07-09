from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from proxy_learner.domain import to_rule_line, to_rule_target
from proxy_learner.probe import confirm_outcome
from proxy_learner.rules import RuleStore
from proxy_learner.state import LearnerState


class Learner:
    def __init__(
        self,
        rules_path: str | Path,
        state_path: str | Path,
        sighting_threshold: int = 3,
        probe: Callable[[str], bool] | None = None,
        reload_provider: Callable[[], None] | None = None,
        probe_attempts: int = 3,
        probe_required_successes: int = 2,
        probe_timeout_seconds: float = 5.0,
    ) -> None:
        self.rules = RuleStore(rules_path)
        self.state = LearnerState(state_path, sighting_threshold=sighting_threshold)
        self._probe = probe
        self._reload_provider = reload_provider
        self._probe_attempts = probe_attempts
        self._probe_required_successes = probe_required_successes
        self._probe_timeout_seconds = probe_timeout_seconds
        self._seen_connection_ids: set[str] = set()

    def handle_proxied_host(self, host: str) -> bool:
        host = host.lower()
        rule_type, target = to_rule_target(host)
        if self.rules.has_rule(rule_type, target):
            return False

        self.state.record_sighting(target)
        if not self.state.is_ready_for_probe(target):
            return False

        if not self._run_probe(host):
            self.state.mark_probed(target)
            return False

        added = self.rules.add_rule(to_rule_line(host))
        self.state.mark_probed(target)
        if added and self._reload_provider is not None:
            self._reload_provider()
        return added

    def handle_direct_failure(
        self,
        host: str,
        probe: Callable[[str], bool] | None = None,
    ) -> bool:
        host = host.lower()
        rule_type, target = to_rule_target(host)
        rule_line = f"{rule_type},{target},DIRECT"
        if rule_line not in self.rules.list_rules():
            return False

        if not self._confirm_direct_failure(host, probe=probe):
            return False

        removed = self.rules.remove_rule(rule_line)
        if removed and self._reload_provider is not None:
            self._reload_provider()
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
