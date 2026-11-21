from pathlib import Path
from typing import Any, Dict, List

from ..validator import Validator
from ..schema_mapper import SchemaMapper
from ..dataset_manager import DatasetManager


class CleaningStage:
    def process(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cleaned_rows: List[Dict[str, Any]] = []
        seen = set()
        for row in rows:
            normalized_row = {k: Validator.normalize_text(v) for k, v in row.items()}
            if not any(normalized_row.values()):
                continue
            row_key = tuple(sorted(normalized_row.items()))
            if row_key in seen:
                continue
            seen.add(row_key)
            cleaned_rows.append(normalized_row)
        return cleaned_rows


class NormalizationStage:
    def process(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        for row in rows:
            normalized.append({k.lower().strip(): Validator.normalize_text(v) for k, v in row.items()})
        return normalized


class EntityExtractionStage:
    def extract(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        entities: list[dict[str, Any]] = []
        for row in rows:
            text = ' '.join(str(value) for value in row.values())
            for token in text.split():
                if token.istitle() and len(token) > 1:
                    entities.append({'entity': token, 'type': 'unknown', 'source': row.get('source', '')})
        return entities


class TopicDetectionStage:
    def detect(self, rows: List[Dict[str, Any]], file_name: str, subject: str) -> Dict[str, Any]:
        score = 0.0
        topic = subject or Path(file_name).stem
        if topic:
            score = 0.75
        if file_name.lower().endswith('.md') or file_name.lower().endswith('.txt'):
            score = max(score, 0.55)
        return {'topic': topic, 'confidence': score}


class StructuringStage:
    def structure(self, rows: List[Dict[str, Any]], source: str, topic: str, confidence: float) -> List[Dict[str, Any]]:
        structured: List[Dict[str, Any]] = []
        for row in rows:
            item = {
                'name': row.get('title') or row.get('name') or row.get('subject') or source,
                'subject': topic,
                'description': row.get('description') or row.get('body') or row.get('content') or '',
                'source': source,
                'confidence': confidence,
                'data': row,
            }
            structured.append(item)
        return structured


class MetadataStage:
    def create(self, source: str, file_name: str, file_type: str, topic: str, confidence: float, record_count: int, entities: List[Dict[str, Any]], status: str) -> Dict[str, Any]:
        from datetime import datetime

        return {
            'source': source,
            'file_name': file_name,
            'file_type': file_type,
            'subject': topic,
            'version': 1,
            'import_date': datetime.utcnow().isoformat(),
            'record_count': record_count,
            'confidence': confidence,
            'entities': entities,
            'topics': [topic] if topic else [],
            'status': status,
        }


class IndexingStage:
    def process(self, dataset_manager: DatasetManager, dataset_name: str) -> None:
        dataset_manager.load_dataset(dataset_name)
