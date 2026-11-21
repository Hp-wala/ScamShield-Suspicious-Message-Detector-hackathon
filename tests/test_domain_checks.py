from src.threat.domain_checks import is_public_host, deep_scan_url, fake_website_detector


def test_private_ip_blocked():
    assert not is_public_host("127.0.0.1")
    assert not is_public_host("10.0.0.1")


def test_missing_optional_api_keys_skip():
    result = deep_scan_url("http://example.com")
    assert result["safe_browsing"]["status"] in {"skipped", "network_error", "ok"}
    assert result["virustotal"]["status"] in {"skipped", "network_error", "ok"}


def test_fake_website_score():
    result = fake_website_detector("sbi-verify.xyz", 5, True, "invalid")
    assert result["score"] >= 80
