from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.core.knowledge_pipeline.base_extractor import BaseExtractor
from src.core.knowledge_pipeline.extractor_registry import registry
from src.core.schema_mapper import SchemaMapper
from src.core.validator import Validator


class MdExtractor(BaseExtractor):
    def validate(self, path: Path) -> bool:
        return path.suffix.lower() == '.md' and path.exists()

    def extract(self, path: Path) -> Tuple[Optional[List[Dict[str, Any]]], Dict[str, Any]]:
        import re

        try:
            raw = path.read_text(encoding='utf-8', errors='ignore')
            text = re.sub(r'```.*?```', ' ', raw, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            if not text.strip():
                return None, {'status': 'empty'}
            row = {'title': path.stem, 'description': Validator.normalize_text(text)}
            schema_mapper = SchemaMapper()
            header_map = schema_mapper.map_headers(row.keys())
            if header_map is None:
                return None, {'status': 'unmapped'}
            return [schema_mapper.map_row(row, header_map)], {'status': 'ok'}
        except Exception as exc:
            return None, {'status': 'error', 'reason': str(exc)}

    def metadata(self, path: Path) -> Dict[str, Any]:
        from ..stages import MetadataStage

        return MetadataStage().create(str(path), path.name, 'md', path.stem, 0.8, 0, [], 'pending')


registry.register('md', MdExtractor())
