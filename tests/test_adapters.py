from src.threat.adapters import SmsAdapter, WhatsappAdapter, EmailAdapter, UrlAdapter, registry
from src.threat.pipeline import analyze
from src.threat.engine import ThreatEngine


def test_sms_adapter_and_registry():
    assert registry.get("sms").validate("Hello")
    assert analyze("sms", "Aapka account blocked hai")[1]


def test_whatsapp_chat_export_parser():
    text = (
        "12/03/24, 9:41 pm - Ravi: UPI collect request. Share OTP.\n"
        "12/03/24, 9:42 pm - Me: No, I will not.\n"
        "<Media omitted>"
    )
    result = ThreatEngine().analyze_chat(text)
    assert result["type"] == "chat"
    assert result["chat"]["total"] == 2
    assert result["messages"][0]["sender"] == "Ravi"


def test_whatsapp_bracket_export_parser():
    text = "[12/03/2024, 21:41:05] Ravi: Your parcel is on hold"
    result = ThreatEngine().analyze_chat(text)
    assert result["chat"]["total"] == 1
    assert result["messages"][0]["timestamp"].startswith("12/")


def test_email_plain_and_attachment_metadata():
    raw = (
        "From: Bank Support <alerts@example.com>\r\n"
        "Reply-To: security@evil.xyz\r\n"
        "Subject: KYC suspended\r\n"
        "MIME-Version: 1.0\r\n"
        "Content-Type: text/plain\r\n\r\n"
        "Your account is blocked. Send OTP to verify."
    )
    parsed = EmailAdapter().extract(raw)
    assert parsed["meta"]["reply_to"] == "security@evil.xyz"
    assert "KYC" in parsed["text"] or "account" in parsed["text"]


def test_url_adapter_extracts_bare_input():
    extracted = UrlAdapter().extract("amaz0n-verify.xyz")
    assert "amaz0n-verify.xyz" in extracted["text"]
