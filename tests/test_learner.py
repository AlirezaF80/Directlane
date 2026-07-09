from proxy_learner.learner import Learner


def test_promote_domain_on_first_sighting(tmp_path):
    rules_path = tmp_path / "learned-direct.json"
    state_path = tmp_path / "state.json"
    learner = Learner(
        rules_path=rules_path,
        state_path=state_path,
        probe=lambda host: True,
        on_rules_changed=lambda: None,
    )

    learner.handle_proxied_host("www.example.com")

    assert learner.rules.has_rule("www.example.com") is True


def test_does_not_reprobe_after_failed_probe(tmp_path, mocker):
    rules_path = tmp_path / "learned-direct.json"
    state_path = tmp_path / "state.json"
    probe = mocker.Mock(return_value=False)
    learner = Learner(
        rules_path=rules_path,
        state_path=state_path,
        probe=probe,
        on_rules_changed=lambda: None,
    )

    learner.handle_proxied_host("www.example.com")
    learner.handle_proxied_host("www.example.com")

    assert probe.call_count == 3
    assert learner.rules.list_domains() == []


def test_each_host_is_learned_separately(tmp_path):
    rules_path = tmp_path / "learned-direct.json"
    state_path = tmp_path / "state.json"
    learner = Learner(
        rules_path=rules_path,
        state_path=state_path,
        probe=lambda host: True,
        on_rules_changed=lambda: None,
    )

    learner.handle_proxied_host("www.example.com")
    learner.handle_proxied_host("api.example.com")

    assert learner.rules.has_rule("www.example.com") is True
    assert learner.rules.has_rule("api.example.com") is True


def test_revoke_learned_domain_on_direct_failure(tmp_path, mocker):
    rules_path = tmp_path / "learned-direct.json"
    state_path = tmp_path / "state.json"
    learner = Learner(
        rules_path=rules_path,
        state_path=state_path,
        probe=lambda host: True,
        on_rules_changed=lambda: None,
    )
    learner.rules.add_rule("blocked.example.com")

    learner.handle_direct_failure(
        "blocked.example.com",
        probe=mocker.Mock(side_effect=[False, False, True]),
    )

    assert learner.rules.has_rule("blocked.example.com") is False
    assert learner.state.was_probed("blocked.example.com") is False
