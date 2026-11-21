import hashlib
import re
from urllib.parse import urlparse

from src.core.validator import Validator
from .adapters import ADAPTERS


class ThreatEngine:
    RULES = {
        "bank": (
            18,
            (
                r"\b(bank|rbi|sbi|hdfc|icici|axis|upi|account|kyc|atm|card)\b",
                r"\b(verify|update|blocked|frozen|suspend|otp)\b",
            ),
        ),
        "delivery": (
            16,
            (
                r"\b(parcel|package|delivery|courier|shipment|customs|delivered)\b",
                r"\b(address|fee|pay|paytm|cod|retry|pending)\b",
            ),
        ),
        "government": (
            18,
            (
                r"\b(gov|government|income tax|police|court|pan|aadhaar|aadhaar|epfo)\b",
                r"\b(penalty|fine|arrest|warrant|legal action|prize|refund)\b",
            ),
        ),
        "job": (
            14,
            (
                r"\b(job|work from home|earning|income|salary|registration fee)\b",
                r"\b(telegram|whatsapp|pay fee|gift card|easy money)\b",
            ),
        ),
        "lottery": (
            20,
            (
                r"\b(prize|lottery|winner|won|reward|cashback|bonus)\b",
                r"\b(claim|lucky|gift|crore|lakhs)\b",
            ),
        ),
    }

    URGENCY = (
        r"\b(urgent|immediately|today|now|within \d+|24 hours|last chance|jaldi|turant|abhi)\b"
    )
    CREDENTIAL_REQUEST = (
        r"\b(otp|pin|password|cvv|card number|aadhar|aadhaar|pan|upi pin|"
        r"don'?t share|share)\b"
    )
    LINK_PATTERN = re.compile(r"https?://[^\s]+|www\.[^\s]+", re.I)
    SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "cutt.ly"}

    def analyze(self, text: str, channel: str = "sms"):
        raw = Validator.normalize_text(text)
        adapter = ADAPTERS.get(channel, ADAPTERS["sms"])
        normalized = adapter.normalize(raw).lower()
        normalized = re.sub(r"\b(b[ae]nk)\b", "bank", normalized)
        normalized = re.sub(r"[^\w@./:+?-]", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()

        score = 0
        reasons = []
        if len(normalized) < 5:
            return self._result(channel, normalized, 0, "low_risk", ["No sufficient message content"])

        category = "general"
        category_score = 0
        for candidate, (weight, patterns) in self.RULES.items():
            matches = sum(bool(re.search(pattern, normalized, re.I)) for pattern in patterns)
            if matches:
                candidate_score = weight + (5 * (matches - 1))
                if candidate_score > category_score:
                    category_score = candidate_score
                    category = candidate
        if category_score:
            score += category_score
            reasons.append(f"Message matches common {category} scam language")

        if re.search(self.URGENCY, normalized, re.I):
            score += 12
            reasons.append("Creates artificial urgency")
        if re.search(self.CREDENTIAL_REQUEST, normalized, re.I):
            score += 18
            reasons.append("Requests sensitive credentials or an OTP")

        urls = self.LINK_PATTERN.findall(normalized)
        if urls:
            score += 10
            reasons.append("Contains an external link")
            for url in urls:
                parsed = urlparse(url if "://" in url else "http://" + url)
                host = (parsed.hostname or "").lower()
                if not url.lower().startswith("https://"):
                    score += 12
                    reasons.append("Uses a non-HTTPS link")
                if re.match(r"^\d{1,3}(?:\.\d{1,3}){3}$", host):
                    score += 18
                    reasons.append("Uses an IP address instead of a trusted domain")
                if host in self.SHORTENERS:
                    score += 12
                    reasons.append("Uses a shortened link")
                if "xn--" in host:
                    score += 16
                    reasons.append("Uses a potentially deceptive internationalized domain")
                if host.count("-") >= 2 or len(host.split(".")) >= 5:
                    score += 8
                    reasons.append("Uses an unusually complex domain")

        if re.search(r"\b(click|tap|open|download|verify|confirm|claim)\b", normalized, re.I):
            score += 8
            reasons.append("Uses a high-pressure action prompt")

        score = max(0, min(100, score))
        if score >= 70:
            label = "high_risk"
        elif score >= 35:
            label = "suspicious"
        else:
            label = "low_risk"
        if not reasons:
            reasons = ["No strong scam indicators detected"]
        return self._result(channel, normalized, score, label, reasons, category)

    def _result(self, channel, normalized, score, label, reasons, category="general"):
        text_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        return {
            "channel": channel,
            "category": category,
            "risk_score": score,
            "risk_level": label,
            "reasons": reasons,
            "text_hash": text_hash,
        }
