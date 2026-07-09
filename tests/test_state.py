from proxy_learner.state import LearnerState


def test_record_sighting_increments_count(tmp_path):
    state_path = tmp_path / "state.json"
    state = LearnerState(state_path)

    assert state.record_sighting("example.com") == 1
    assert state.record_sighting("example.com") == 2


def test_is_ready_for_probe_after_threshold(tmp_path):
    state_path = tmp_path / "state.json"
    state = LearnerState(state_path, sighting_threshold=3)

    state.record_sighting("example.com")
    state.record_sighting("example.com")
    assert state.is_ready_for_probe("example.com") is False

    state.record_sighting("example.com")
    assert state.is_ready_for_probe("example.com") is True


def test_mark_probed_clears_sighting_count(tmp_path):
    state_path = tmp_path / "state.json"
    state = LearnerState(state_path, sighting_threshold=2)
    state.record_sighting("example.com")
    state.record_sighting("example.com")

    state.mark_probed("example.com")
    assert state.is_ready_for_probe("example.com") is False
    assert state.get_sighting_count("example.com") == 0


def test_persistence_across_instances(tmp_path):
    state_path = tmp_path / "state.json"
    state = LearnerState(state_path, sighting_threshold=3)
    state.record_sighting("example.com")
    state.record_sighting("example.com")

    reloaded = LearnerState(state_path, sighting_threshold=3)
    assert reloaded.get_sighting_count("example.com") == 2
