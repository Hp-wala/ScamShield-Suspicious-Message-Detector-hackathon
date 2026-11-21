from typing import Any, Dict, List

from src.core.validator import Validator


class NormalizationStage:
    def process(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized_rows: List[Dict[str, Any]] = []

        for row in rows:
            normalized: Dict[str, str] = {}
            for key, value in row.items():
                key_name = str(key).strip().lower()
                text_value = Validator.normalize_text(value)
                normalized[key_name] = text_value

                if key_name in ('title', 'name', 'subject', 'topic'):
                    normalized[key_name] = text_value.title()
                elif key_name in ('description', 'body', 'content'):
                    normalized[key_name] = text_value.strip()

            normalized_rows.append(normalized)

        return normalized_rows
