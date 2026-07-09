from proxy_learner.domain import to_rule_line, to_rule_target


def test_to_rule_target_strips_www_suffix():
    assert to_rule_target("www.digikala.com") == (
        "DOMAIN-SUFFIX",
        "digikala.com",
    )


def test_to_rule_target_strips_cdn_suffix():
    assert to_rule_target("cdn.something.io") == (
        "DOMAIN-SUFFIX",
        "something.io",
    )


def test_to_rule_target_strips_api_suffix():
    assert to_rule_target("api.github.com") == ("DOMAIN-SUFFIX", "github.com")


def test_to_rule_target_two_label_domain():
    assert to_rule_target("github.com") == ("DOMAIN-SUFFIX", "github.com")


def test_to_rule_target_subdomain_without_known_prefix():
    assert to_rule_target("raw.githubusercontent.com") == (
        "DOMAIN-SUFFIX",
        "githubusercontent.com",
    )


def test_to_rule_target_ip_uses_exact_domain():
    assert to_rule_target("8.8.8.8") == ("DOMAIN", "8.8.8.8")


def test_to_rule_line_formats_clash_rule():
    assert to_rule_line("www.example.com") == "DOMAIN-SUFFIX,example.com,DIRECT"
