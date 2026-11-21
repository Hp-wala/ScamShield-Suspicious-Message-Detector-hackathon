from src.threat.extras import (
    expand_shortforms, remove_repeated_chars, detect_language,
    extract_money, extract_emails, detect_obfuscation,
    detect_mixed_script, remove_emoji, digit_ratio,
)
from src.threat.scorer import score_message


def test_shortforms_and_repeated_chars():
    assert "please" in expand_shortforms("pls")
    assert remove_repeated_chars("urgenttttt") == "urgent"


def test_language_money_email_and_emoji():
    assert detect_language("NAMASTE  hello") == "hinglish"
    assert "Rs 2500" in extract_money("Pay Rs 2500 now")[0]
    assert extract_emails("Contact fake@example.com")[0] == "fake@example.com"
    assert "hello" in remove_emoji("hello😀")


def test_obfuscation_mixed_script_and_ratio():
    assert detect_obfuscation("b@nk 0TP cl1ck")["detected"]
    assert detect_mixed_script("bank БАNK")["homoglyph"]
    assert digit_ratio("12345hello") > 0.4


def test_new_signals_feed_scorer():
    result = score_message("sms", "URGENTT 0TP verify b@nk at cl1ck")
    ids = {signal["id"] for signal in result["signals"]}
    assert "obfuscation" in ids
