import json

from proxy_learner.rules import KaringRuleStore


def test_empty_store_has_no_rules(tmp_path):
    store = KaringRuleStore(tmp_path / "learned-direct.json")
    assert store.list_domain_suffixes() == []
    assert store.list_domains() == []


def test_add_suffix_persists_to_file(tmp_path):
    path = tmp_path / "learned-direct.json"
    store = KaringRuleStore(path)
    assert store.add_rule("DOMAIN-SUFFIX", "example.com") is True

    reloaded = KaringRuleStore(path)
    assert reloaded.list_domain_suffixes() == [".example.com"]


def test_add_suffix_is_idempotent(tmp_path):
    path = tmp_path / "learned-direct.json"
    store = KaringRuleStore(path)
    store.add_rule("DOMAIN-SUFFIX", "example.com")
    assert store.add_rule("DOMAIN-SUFFIX", "example.com") is False
    assert store.list_domain_suffixes() == [".example.com"]


def test_remove_suffix(tmp_path):
    path = tmp_path / "learned-direct.json"
    store = KaringRuleStore(path)
    store.add_rule("DOMAIN-SUFFIX", "example.com")
    store.add_rule("DOMAIN-SUFFIX", "other.com")

    assert store.remove_rule("DOMAIN-SUFFIX", "example.com") is True
    assert store.list_domain_suffixes() == [".other.com"]


def test_has_rule_matches_type_and_target(tmp_path):
    path = tmp_path / "learned-direct.json"
    store = KaringRuleStore(path)
    store.add_rule("DOMAIN-SUFFIX", "example.com")

    assert store.has_rule("DOMAIN-SUFFIX", "example.com") is True
    assert store.has_rule("DOMAIN", "www.example.com") is False


def test_writes_karing_import_format(tmp_path):
    path = tmp_path / "learned-direct.json"
    store = KaringRuleStore(path, group_name="learned-direct")
    store.add_rule("DOMAIN-SUFFIX", "cursor.sh")

    data = json.loads(path.read_text(encoding="utf-8"))
    rule = data["rules"][0]
    assert rule["outbound"] == "direct"
    assert rule["name"] == "learned-direct"
    assert rule["domain_suffix"] == [".cursor.sh"]
