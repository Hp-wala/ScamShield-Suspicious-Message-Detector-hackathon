import re
from typing import Any


class Validator:
    @staticmethod
    def normalize_text(value: Any) -> str:
        if value is None:
            return ""
        text = str(value)
        text = re.sub(r"<[^>]*>", " ", text)
        text = text.replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n+", "\n", text)
        return text.strip()

    @staticmethod
    def is_valid_string(value: Any) -> bool:
        return isinstance(value, str) and bool(value.strip())
