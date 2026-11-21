from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.core.knowledge_pipeline.base_extractor import BaseExtractor
from src.core.knowledge_pipeline.extractor_registry import registry
from src.core.schema_mapper import SchemaMapper
from src.core.validator import Validator


class JsonExtractor(BaseExtractor):
    def validate(self, path: Path) -> bool:
        return path.suffix.lower() == '.json' and path.exists()

    def extract(self, path: Path) -> Tuple[Optional[List[Dict[str, Any]]], Dict[str, Any]]:
        import json

        try:
            payload = json.loads(path.read_text(encoding='utf-8'))
            if isinstance(payload, dict):
                payload = [payload]
            if not isinstance(payload, list):
                return None, {'status': 'invalid', 'reason': 'json_not_array'}
            rows: List[Dict[str, Any]] = []
            schema_mapper = SchemaMapper()
            header_map = None
            for item in payload:
                if not isinstance(item, dict):
                    continue
                if header_map is None:
                    header_map = schema_mapper.map_headers(item.keys())
                    if header_map is None:
                        return None, {'status': 'unmapped'}
                cleaned = {k: Validator.normalize_text(v) for k, v in item.items()}
                rows.append(schema_mapper.map_row(cleaned, header_map))
            return rows, {'status': 'ok'}
        except Exception as exc:
            return None, {'status': 'error', 'reason': str(exc)}

    def metadata(self, path: Path) -> Dict[str, Any]:
        from ..stages import MetadataStage

        return MetadataStage().create(str(path), path.name, 'json', path.stem, 0.8, 0, [], 'pending')


registry.register('json', JsonExtractor())
