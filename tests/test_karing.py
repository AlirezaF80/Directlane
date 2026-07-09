from proxy_learner.karing import (
    extract_host,
    is_learned_direct_connection,
    is_proxied_connection,
    KaringClient,
)


def test_extract_host_from_connection_metadata():
    connection = {"metadata": {"host": "WWW.Example.com"}}
    assert extract_host(connection) == "www.example.com"


def test_is_proxied_connection_when_chain_ends_with_proxy():
    connection = {"chains": ["MATCH", "Proxy"]}
    assert is_proxied_connection(connection) is True


def test_is_proxied_connection_when_chain_is_direct():
    connection = {"chains": ["DOMAIN", "DIRECT"]}
    assert is_proxied_connection(connection) is False


def test_is_learned_direct_connection_matches_provider_name():
    connection = {
        "chains": ["RULE-SET", "DIRECT"],
        "rule": "RULE-SET,learned-direct,DIRECT",
        "rulePayload": "learned-direct",
    }
    assert is_learned_direct_connection(connection) is True


def test_get_connections_parses_payload(mocker):
    session = mocker.Mock()
    response = mocker.Mock()
    response.json.return_value = {
        "connections": [{"metadata": {"host": "example.com"}}]
    }
    response.raise_for_status = mocker.Mock()
    session.get.return_value = response

    client = KaringClient("http://127.0.0.1:9093", session=session)
    connections = client.get_connections()

    assert connections == [{"metadata": {"host": "example.com"}}]
    session.get.assert_called_once_with(
        "http://127.0.0.1:9093/connections",
        timeout=10,
    )


def test_reload_rule_provider_calls_put(mocker):
    session = mocker.Mock()
    response = mocker.Mock()
    response.status_code = 204
    response.raise_for_status = mocker.Mock()
    session.put.return_value = response

    client = KaringClient("http://127.0.0.1:9093", session=session)
    assert client.reload_rule_provider("learned-direct") is True

    session.put.assert_called_once_with(
        "http://127.0.0.1:9093/providers/rules/learned-direct",
        timeout=10,
    )
