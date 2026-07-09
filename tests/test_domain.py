from directlane.domain import to_rule_target


def test_to_rule_target_uses_exact_hostname():
    assert to_rule_target("www.digikala.com") == (
        "DOMAIN",
        "www.digikala.com",
    )


def test_to_rule_target_preserves_subdomain():
    assert to_rule_target("api2.cursor.sh") == ("DOMAIN", "api2.cursor.sh")


def test_to_rule_target_preserves_deep_subdomain():
    assert to_rule_target("colab.research.google.com") == (
        "DOMAIN",
        "colab.research.google.com",
    )


def test_to_rule_target_normalizes_case():
    assert to_rule_target("WWW.Example.COM") == ("DOMAIN", "www.example.com")


def test_to_rule_target_ip_uses_exact_domain():
    assert to_rule_target("8.8.8.8") == ("DOMAIN", "8.8.8.8")
