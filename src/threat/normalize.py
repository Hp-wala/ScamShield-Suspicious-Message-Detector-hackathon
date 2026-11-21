"""Text cleaning and hash helpers for ScamShield analysis stages."""
from src.core.validator import Validator


def clean_text(text: str) -> str:
    """Return NFKC-cleaned, lowercase text with control characters removed."""
    return Validator.clean_text(text)


def message_hash(text: str) -> str:
    return Validator.message_hash(text)
