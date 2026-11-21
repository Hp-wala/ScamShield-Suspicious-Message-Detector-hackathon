from typing import Any


class Validator:
    @staticmethod
    def is_valid_string(value: Any) -> bool:
        return isinstance(value, str) and value.strip() != ''

    @staticmethod
    def normalize_text(value: Any) -> str:
        if value is None:
            return ''
        return str(value).strip()

    @staticmethod
    def safe_get(obj: dict, key: str, default: Any = '') -> Any:
        return obj.get(key, default) if isinstance(obj, dict) else default
