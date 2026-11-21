from typing import Any, Dict, List

from src.core.validator import Validator


class CleaningStage:
    def process(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cleaned_rows: List[Dict[str, Any]] = []
        seen = set()

        for row in rows:
            normalized_row: Dict[str, str] = {}
            for key, value in row.items():
                normalized_row[str(key).strip()] = Validator.normalize_text(value)

            if not any(normalized_row.values()):
                continue

            row_key = tuple(sorted(normalized_row.items()))
            if row_key in seen:
                continue
            seen.add(row_key)

            # Normalize missing important fields to make later stages more robust.
            if not normalized_row.get('title') and normalized_row.get('name'):
                normalized_row['title'] = normalized_row['name']
            if not normalized_row.get('description') and normalized_row.get('body'):
                normalized_row['description'] = normalized_row['body']
            if not normalized_row.get('description') and normalized_row.get('content'):
                normalized_row['description'] = normalized_row['content']

            for key, value in list(normalized_row.items()):
                if value is None:
                    normalized_row[key] = ''

            cleaned_rows.append(normalized_row)

        return cleaned_rows
