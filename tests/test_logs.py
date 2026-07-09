from proxy_learner.logs import find_failed_host


def test_find_failed_host_matches_learned_target():
    rules = ["DOMAIN-SUFFIX,example.com,DIRECT"]
    line = "[TCP] dial DIRECT example.com:443 error: i/o timeout"
    assert find_failed_host(line, rules) == "example.com"


def test_find_failed_host_ignores_unrelated_errors():
    rules = ["DOMAIN-SUFFIX,example.com,DIRECT"]
    line = "[TCP] dial DIRECT other.com:443 error: i/o timeout"
    assert find_failed_host(line, rules) is None


def test_find_failed_host_requires_direct_in_log_line():
    rules = ["DOMAIN-SUFFIX,example.com,DIRECT"]
    line = "[TCP] dial PROXY example.com:443 error: i/o timeout"
    assert find_failed_host(line, rules) is None


def test_find_failed_host_requires_failure_keyword():
    rules = ["DOMAIN-SUFFIX,example.com,DIRECT"]
    line = "[TCP] connected to example.com:443"
    assert find_failed_host(line, rules) is None
