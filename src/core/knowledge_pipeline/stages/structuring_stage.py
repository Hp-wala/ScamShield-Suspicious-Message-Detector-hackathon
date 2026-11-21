from typing import Any, Dict, List

from src.core.validator import Validator


class StructuringStage:
    def structure(self, rows: List[Dict[str, Any]], source: str, topic: str, confidence: float) -> List[Dict[str, Any]]:
        structured: List[Dict[str, Any]] = []

        for index, row in enumerate(rows):
            record = {
                'id': row.get('id') or f'{source}:{index}',
                'title': row.get('title') or row.get('name') or source,
                'description': row.get('description') or row.get('body') or row.get('content') or '',
                'category': row.get('category', ''),
                'label': row.get('label', ''),
                'value': row.get('value', ''),
                'topic': topic,
                'source': source,
                'confidence': confidence,
                'metadata': {k: v for k, v in row.items() if k not in {'id', 'title', 'description', 'category', 'label', 'value'}},
            }
            structured.append({k: Validator.normalize_text(v) if isinstance(v, str) else v for k, v in record.items()})

        return structured
