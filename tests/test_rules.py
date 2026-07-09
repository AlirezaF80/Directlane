import json

from proxy_learner.rules import KaringRuleStore


def test_empty_store_has_no_rules(tmp_path):
    store = KaringRuleStore(tmp_path / "learned-direct.json")
    assert store.list_domain_suffixes() == []
    assert store.list_domains() == []


def test_add_domain_persists_to_file(tmp_path):
    path = tmp_path / "learned-direct.json"
    store = KaringRuleStore(path)
    assert store.add_rule("DOMAIN", "api2.cursor.sh") is True

    reloaded = KaringRuleStore(path)
    assert reloaded.list_domains() == ["api2.cursor.sh"]


def test_add_domain_is_idempotent(tmp_path):
    path = tmp_path / "learned-direct.json"
    store = KaringRuleStore(path)
    store.add_rule("DOMAIN", "api2.cursor.sh")
    assert store.add_rule("DOMAIN", "api2.cursor.sh") is False
    assert store.list_domains() == ["api2.cursor.sh"]


def test_remove_domain(tmp_path):
    path = tmp_path / "learned-direct.json"
    store = KaringRuleStore(path)
    store.add_rule("DOMAIN", "api2.cursor.sh")
    store.add_rule("DOMAIN", "other.example.com")

    assert store.remove_rule("DOMAIN", "api2.cursor.sh") is True
    assert store.list_domains() == ["other.example.com"]


def test_has_rule_matches_exact_domain(tmp_path):
    path = tmp_path / "learned-direct.json"
    store = KaringRuleStore(path)
    store.add_rule("DOMAIN", "api2.cursor.sh")

    assert store.has_rule("DOMAIN", "api2.cursor.sh") is True
    assert store.has_rule("DOMAIN", "cursor.sh") is False


def test_writes_karing_import_format(tmp_path):
    path = tmp_path / "learned-direct.json"
    store = KaringRuleStore(path, group_name="learned-direct")
    store.add_rule("DOMAIN", "api2.cursor.sh")

    data = json.loads(path.read_text(encoding="utf-8"))
    rule = data["rules"][0]
    assert rule["outbound"] == "direct"
    assert rule["name"] == "learned-direct"
    assert rule["domain"] == ["api2.cursor.sh"]
    assert "domain_suffix" not in rule
