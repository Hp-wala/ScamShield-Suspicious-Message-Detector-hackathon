from src.threat.breach_checks import email_breach_check, password_breach_check, phone_breach_check


def test_breach_missing_key_skips(monkeypatch):
    monkeypatch.delenv("HIBP_API_KEY", raising=False)
    assert email_breach_check("test@example.com")["status"] == "skipped"


def test_password_missing_skips():
    assert password_breach_check("")["status"] == "skipped"


def test_phone_explicitly_not_supported():
    assert phone_breach_check("0000000000")["status"] == "not_supported"
