from proxy_learner.rules import RuleStore


def test_empty_store_has_no_rules(tmp_path):
    rules_path = tmp_path / "learned-direct.yaml"
    store = RuleStore(rules_path)
    assert store.list_rules() == []


def test_add_rule_persists_to_file(tmp_path):
    rules_path = tmp_path / "learned-direct.yaml"
    store = RuleStore(rules_path)
    store.add_rule("DOMAIN-SUFFIX,example.com,DIRECT")

    reloaded = RuleStore(rules_path)
    assert reloaded.list_rules() == ["DOMAIN-SUFFIX,example.com,DIRECT"]


def test_add_rule_is_idempotent(tmp_path):
    rules_path = tmp_path / "learned-direct.yaml"
    store = RuleStore(rules_path)
    store.add_rule("DOMAIN-SUFFIX,example.com,DIRECT")
    store.add_rule("DOMAIN-SUFFIX,example.com,DIRECT")

    assert store.list_rules() == ["DOMAIN-SUFFIX,example.com,DIRECT"]


def test_remove_rule(tmp_path):
    rules_path = tmp_path / "learned-direct.yaml"
    store = RuleStore(rules_path)
    store.add_rule("DOMAIN-SUFFIX,example.com,DIRECT")
    store.add_rule("DOMAIN-SUFFIX,other.com,DIRECT")

    removed = store.remove_rule("DOMAIN-SUFFIX,example.com,DIRECT")
    assert removed is True
    assert store.list_rules() == ["DOMAIN-SUFFIX,other.com,DIRECT"]


def test_remove_missing_rule_returns_false(tmp_path):
    rules_path = tmp_path / "learned-direct.yaml"
    store = RuleStore(rules_path)
    assert store.remove_rule("DOMAIN-SUFFIX,missing.com,DIRECT") is False


def test_has_rule_matches_type_and_target(tmp_path):
    rules_path = tmp_path / "learned-direct.yaml"
    store = RuleStore(rules_path)
    store.add_rule("DOMAIN-SUFFIX,example.com,DIRECT")

    assert store.has_rule("DOMAIN-SUFFIX", "example.com") is True
    assert store.has_rule("DOMAIN", "www.example.com") is False
