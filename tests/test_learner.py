from proxy_learner.learner import Learner


def test_promote_domain_after_threshold_and_successful_probe(tmp_path):
    rules_path = tmp_path / "learned-direct.yaml"
    state_path = tmp_path / "state.json"
    learner = Learner(
        rules_path=rules_path,
        state_path=state_path,
        sighting_threshold=3,
        probe=lambda host: True,
        reload_provider=lambda: None,
    )

    for _ in range(3):
        learner.handle_proxied_host("www.example.com")

    assert learner.rules.has_rule("DOMAIN-SUFFIX", "example.com") is True


def test_sightings_aggregate_by_rule_target(tmp_path):
    rules_path = tmp_path / "learned-direct.yaml"
    state_path = tmp_path / "state.json"
    learner = Learner(
        rules_path=rules_path,
        state_path=state_path,
        sighting_threshold=3,
        probe=lambda host: True,
        reload_provider=lambda: None,
    )

    learner.handle_proxied_host("www.example.com")
    learner.handle_proxied_host("api.example.com")
    learner.handle_proxied_host("cdn.example.com")

    assert learner.rules.has_rule("DOMAIN-SUFFIX", "example.com") is True


def test_does_not_promote_before_threshold(tmp_path, mocker):
    rules_path = tmp_path / "learned-direct.yaml"
    state_path = tmp_path / "state.json"
    probe = mocker.Mock(return_value=True)
    learner = Learner(
        rules_path=rules_path,
        state_path=state_path,
        sighting_threshold=3,
        probe=probe,
        reload_provider=lambda: None,
    )

    learner.handle_proxied_host("www.example.com")
    learner.handle_proxied_host("www.example.com")

    probe.assert_not_called()
    assert learner.rules.list_rules() == []


def test_failed_probe_does_not_add_rule(tmp_path):
    rules_path = tmp_path / "learned-direct.yaml"
    state_path = tmp_path / "state.json"
    learner = Learner(
        rules_path=rules_path,
        state_path=state_path,
        sighting_threshold=2,
        probe=lambda host: False,
        reload_provider=lambda: None,
    )

    learner.handle_proxied_host("www.example.com")
    learner.handle_proxied_host("www.example.com")

    assert learner.rules.list_rules() == []


def test_revoke_learned_domain_on_direct_failure(tmp_path, mocker):
    rules_path = tmp_path / "learned-direct.yaml"
    state_path = tmp_path / "state.json"
    learner = Learner(
        rules_path=rules_path,
        state_path=state_path,
        sighting_threshold=2,
        probe=lambda host: True,
        reload_provider=lambda: None,
    )
    learner.rules.add_rule("DOMAIN-SUFFIX,blocked.com,DIRECT")

    learner.handle_direct_failure(
        "blocked.com",
        probe=mocker.Mock(side_effect=[False, False, True]),
    )

    assert learner.rules.has_rule("DOMAIN-SUFFIX", "blocked.com") is False
