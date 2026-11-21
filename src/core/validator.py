import re
import unicodedata
import hashlib
from typing import Any


class Validator:
    @staticmethod
    def normalize_text(value: Any) -> str:
        if value is None:
            return ""
        text = unicodedata.normalize("NFKC", str(value))
        text = text.replace("\u200b", "").replace("\ufeff", "")
        text = "".join(ch for ch in text if ch.isprintable() or ch in "\n\t ")
        text = re.sub(r"<[^>]*>", " ", text)
        text = text.replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n+", "\n", text)
        return text.strip()

    @staticmethod
    def clean_text(value: Any) -> str:
        return re.sub(r"\s+", " ", Validator.normalize_text(value)).lower()

    @staticmethod
    def validate_text(value: Any, max_length: int = 5000) -> bool:
        return isinstance(value, str) and bool(value.strip()) and len(value) <= max_length

    @staticmethod
    def message_hash(value: Any) -> str:
        return hashlib.sha256(Validator.clean_text(value).encode("utf-8")).hexdigest()

    @staticmethod
    def is_valid_string(value: Any) -> bool:
        return isinstance(value, str) and bool(value.strip())
