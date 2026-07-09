import json

from proxy_learner.karing_discovery import discover_karing


def test_discover_karing_reads_control_port_and_secret(tmp_path):
    service_json = tmp_path / "service.json"
    service_json.write_text(
        json.dumps({"control_port": 3057, "secret": "abc123"}),
        encoding="utf-8",
    )

    discovered = discover_karing(service_json)

    assert discovered is not None
    assert discovered.api_url == "http://127.0.0.1:3057"
    assert discovered.secret == "abc123"


def test_discover_karing_returns_none_for_missing_file(tmp_path):
    assert discover_karing(tmp_path / "missing.json") is None
