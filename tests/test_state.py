from proxy_learner.state import ProbeState


def test_mark_probed_records_host(tmp_path):
    state_path = tmp_path / "state.json"
    state = ProbeState(state_path)

    state.mark_probed("example.com")

    assert state.was_probed("example.com") is True
    assert state.was_probed("other.com") is False


def test_clear_allows_reprobe(tmp_path):
    state_path = tmp_path / "state.json"
    state = ProbeState(state_path)
    state.mark_probed("example.com")

    state.clear("example.com")

    assert state.was_probed("example.com") is False


def test_persistence_across_instances(tmp_path):
    state_path = tmp_path / "state.json"
    state = ProbeState(state_path)
    state.mark_probed("example.com")

    reloaded = ProbeState(state_path)
    assert reloaded.was_probed("example.com") is True
