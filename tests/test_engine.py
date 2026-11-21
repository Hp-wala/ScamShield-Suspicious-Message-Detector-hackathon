from src.threat.engine import ThreatEngine


def test_bank_otp_message_is_high_risk():
    result = ThreatEngine().analyze(
        "Aapka SBI account blocked hai. Turant KYC verify karein aur OTP share karein: http://192.0.2.1/verify",
        "sms",
    )
    assert result["category"] == "bank"
    assert result["risk_score"] >= 70
    assert result["risk_level"] == "high_risk"


def test_normal_message_is_low_risk():
    result = ThreatEngine().analyze("Meeting kal shaam 6 baje office mein hai.", "whatsapp")
    assert result["risk_score"] < 35
    assert result["risk_level"] == "low_risk"


def test_text_is_not_returned_and_hash_is_normalized():
    text = "  YOUR BANK  account is blocked  "
    result = ThreatEngine().analyze(text, "email")
    assert "text" not in result
    assert "raw" not in result
    assert len(result["text_hash"]) == 64
