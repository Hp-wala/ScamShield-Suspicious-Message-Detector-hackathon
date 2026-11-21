import pytest

from src.threat.engine import ThreatEngine
from src.threat.normalize import clean_text, message_hash
from src.threat import rules, brands, urls, scorer, advice, pipeline


engine = ThreatEngine()

SCAMS = [
    "Aapka SBI account blocked hai, turant KYC update karo aur OTP share karo.",
    "Congratulations! You won a lottery reward. Pay Rs 500 processing fee to claim.",
    "Your parcel is on hold. Confirm address and pay redelivery fee: http://192.168.1.10/pay",
    "Bijli bill pending hai. Electricity disconnect tonight. Pay Rs 999 registration fee immediately.",
    "Income tax refund pending. Click to verify PAN and Aadhaar and share OTP.",
    "Ghar baithe daily Rs 3000 job. No experience needed, join Telegram.",
    "Guaranteed returns: double your money. Join VIP crypto profit group and pay Rs 500.",
    "UPI collect request: accept this request to receive Rs 5000. Share UPI PIN now.",
    "You are under digital arrest. Stay on video call and share OTP. Do not tell anyone.",
    ".apk download link plus AnyDesk installation required. Share OTP.",
    "Hi Mum, new number. Please send me Rs 2000 and OTP urgently.",
    "Call 9876543210 immediately and share OTP.",
    "Join my WhatsApp group on t.me/earn and verify KYC with OTP, send Rs 500 registration fee.",
    "Lucky draw winner: claim prize now with Aadhaar and PAN. Share OTP.",
    "Customs parcel stuck. Pay Rs 1200 to release.",
    "Amazon account suspended. Verify account at amaz0n-verify.xyz.",
    "CBI narcotics parcel found. Stay on video call, pay security charges.",
    "Aaj hi card suspended ho jayega. Turant UPI PIN aur OTP share karo.",
    "PM Kisan subsidy stopped. Update Aadhaar and bank UPI PIN.",
    "Stock tips VIP group guaranteed 2% daily returns, send registration fee.",
]

GENUINE = [
    "Meeting kal shaam 6 baje office mein hai.",
    "Do not share this OTP. The bank never asks for it.",
    "Rs 499 debited from a/c XX1234. Avl bal Rs 5600.",
    "Your Amazon order was shipped. Track it on amazon.in.",
    "Your parcel was delivered. Thank you for shopping.",
    "Bijli bill is Rs 1240. Pay before the due date at the official app.",
    "You have a Jio recharge plan of 28 days.",
    "Income Tax has received your ITR acknowledgement.",
    "Your OTP is 482910. Use it only on the bank app.",
    "Hi, I reached office; call me after lunch.",
]


@pytest.mark.parametrize("text", SCAMS)
def test_scam_cases(text):
    result = engine.analyze(text)
    assert result["score"] >= 60, (text, result)
    assert result["verdict"] == "Likely Scam"


@pytest.mark.parametrize("text", GENUINE)
def test_genuine_cases(text):
    result = engine.analyze(text)
    assert result["score"] < 30, (text, result)
    assert result["verdict"] == "Safe"


@pytest.mark.parametrize("url", [
    "https://bit.ly/claim",
    "https://tinyurl.com/otp",
    "http://192.168.1.20/login",
    "https://amaz0n-login.xyz",
    "https://sbi-kyc-update.xyz",
    "hxxp://bank-login.top",
    "https://xn--amazn-qva.com",
    "https://a.b.c.d.verify.com",
    "https://sbi-verify.support",
    "https://example.xyz/path",
    "https://t.co/abc",
])
def test_dangerous_url_cases(url):
    result = urls.analyze_url(url)
    assert result["score"] >= 20


@pytest.mark.parametrize("url", [
    "https://sbi.co.in",
    "https://onlinesbi.sbi",
    "https://wa.me/919876543210",
    "https://uidai.gov.in",
    "https://amazon.in",
    "https://icicibank.com",
])
def test_official_urls_safe(url):
    result = urls.analyze_url(url)
    assert result["score"] < 20


def test_phase_two_importable_modules():
    assert callable(clean_text)
    assert len(message_hash("test")) == 64
    assert len(rules.RULES) > 0
    assert len(brands.BRANDS) > 0
    assert callable(urls.extract_urls)
    assert callable(scorer.score_message)
