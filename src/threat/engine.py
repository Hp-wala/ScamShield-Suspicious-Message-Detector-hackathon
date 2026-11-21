from src.core.validator import Validator
from .normalize import clean_text
from .scorer import score_message


class ThreatEngine:
    def analyze(self, text: str, channel: str = "sms", sender: str = ""):
        raw = Validator.normalize_text(text)
        cleaned = clean_text(raw)
        result = score_message(channel, cleaned, sender)
        result.pop("text_hash", None)
        return result
