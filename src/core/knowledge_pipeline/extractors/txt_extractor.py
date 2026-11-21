from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.core.knowledge_pipeline.base_extractor import BaseExtractor
from src.core.knowledge_pipeline.extractor_registry import registry
from src.core.schema_mapper import SchemaMapper
from src.core.validator import Validator


class TxtExtractor(BaseExtractor):
    def validate(self, path: Path) -> bool:
        return path.suffix.lower() == '.txt' and path.exists()

    def extract(self, path: Path) -> Tuple[Optional[List[Dict[str, Any]]], Dict[str, Any]]:
        try:
            raw = path.read_text(encoding='utf-8', errors='ignore')
            if not raw.strip():
                return None, {'status': 'empty'}
            row = {'title': path.stem, 'description': Validator.normalize_text(raw)}
            schema_mapper = SchemaMapper()
            header_map = schema_mapper.map_headers(row.keys())
            if header_map is None:
                return None, {'status': 'unmapped'}
            return [schema_mapper.map_row(row, header_map)], {'status': 'ok'}
        except Exception as exc:
            return None, {'status': 'error', 'reason': str(exc)}

    def metadata(self, path: Path) -> Dict[str, Any]:
        from ..stages import MetadataStage

        return MetadataStage().create(str(path), path.name, 'txt', path.stem, 0.8, 0, [], 'pending')


registry.register('txt', TxtExtractor())
