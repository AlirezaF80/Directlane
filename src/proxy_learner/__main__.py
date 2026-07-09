from __future__ import annotations

import logging
import time
from threading import Event, Thread

from proxy_learner.config import Config
from proxy_learner.karing import KaringClient
from proxy_learner.learner import Learner
from proxy_learner.logs import find_failed_host

logger = logging.getLogger(__name__)


def build_learner(config: Config, client: KaringClient) -> Learner:
    def reload_provider() -> None:
        client.reload_rule_provider(config.rule_provider_name)

    return Learner(
        rules_path=config.rules_path,
        state_path=config.state_path,
        sighting_threshold=config.sighting_threshold,
        reload_provider=reload_provider,
        probe_attempts=config.probe_attempts,
        probe_required_successes=config.probe_required_successes,
        probe_timeout_seconds=config.probe_timeout_seconds,
    )


def poll_connections(learner: Learner, client: KaringClient) -> None:
    connections = client.get_connections()
    learner.process_connections(connections)


def watch_logs(
    learner: Learner,
    client: KaringClient,
    stop_event: Event,
) -> None:
    while not stop_event.is_set():
        try:
            response = client.iter_log_lines(level="warning")
            for raw_line in response.iter_lines(decode_unicode=True):
                if stop_event.is_set():
                    break
                if not raw_line:
                    continue
                host = find_failed_host(raw_line, learner.rules.list_rules())
                if host:
                    learner.handle_direct_failure(host)
        except Exception as exc:
            if stop_event.is_set():
                return
            logger.warning("log watcher error, retrying: %s", exc)
            time.sleep(5)


def run(config: Config | None = None) -> None:
    config = config or Config.from_env()
    client = KaringClient(config.karing_api_url, config.karing_secret)
    learner = build_learner(config, client)
    stop_event = Event()

    log_thread = Thread(
        target=watch_logs,
        args=(learner, client, stop_event),
        daemon=True,
    )
    log_thread.start()

    try:
        while True:
            poll_connections(learner, client)
            time.sleep(config.poll_interval_seconds)
    except KeyboardInterrupt:
        stop_event.set()
        log_thread.join(timeout=2)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    run()
