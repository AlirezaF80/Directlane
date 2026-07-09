from proxy_learner.probe import confirm_outcome, confirm_probe


def test_confirm_probe_requires_two_of_three_successes(mocker):
    mocker.patch(
        "proxy_learner.probe.probe_tls",
        side_effect=[True, True, False],
    )
    assert confirm_probe("example.com") is True


def test_confirm_probe_fails_with_one_of_three_successes(mocker):
    mocker.patch(
        "proxy_learner.probe.probe_tls",
        side_effect=[True, False, False],
    )
    assert confirm_probe("example.com") is False


def test_confirm_outcome_for_revocation_requires_two_of_three_failures(mocker):
    mocker.patch(
        "proxy_learner.probe.probe_tls",
        side_effect=[False, False, True],
    )
    assert confirm_outcome("example.com", expect_success=False) is True
