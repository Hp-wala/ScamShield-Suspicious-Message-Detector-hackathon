from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.core.knowledge_pipeline.base_extractor import BaseExtractor
from src.core.knowledge_pipeline.extractor_registry import registry
from src.core.knowledge_pipeline.stages import MetadataStage
from src.core.schema_mapper import SchemaMapper
from src.core.validator import Validator


class CsvExtractor(BaseExtractor):
    def validate(self, path: Path) -> bool:
        return path.suffix.lower() == '.csv' and path.exists()

    def extract(self, path: Path) -> Tuple[Optional[List[Dict[str, Any]]], Dict[str, Any]]:
        import csv

        rows: List[Dict[str, Any]] = []
        schema_mapper = SchemaMapper()
        try:
            with path.open('r', encoding='utf-8', errors='ignore') as handle:
                reader = csv.DictReader(handle)
                if not reader.fieldnames:
                    return None, {'status': 'invalid', 'reason': 'missing_headers'}
                header_map = schema_mapper.map_headers(reader.fieldnames)
                if header_map is None:
                    return None, {'status': 'unmapped'}
                for raw_row in reader:
                    cleaned = {k: Validator.normalize_text(v) for k, v in raw_row.items()}
                    rows.append(schema_mapper.map_row(cleaned, header_map))
            return rows, {'status': 'ok'}
        except Exception as exc:
            return None, {'status': 'error', 'reason': str(exc)}

    def metadata(self, path: Path) -> Dict[str, Any]:
        return MetadataStage().create(str(path), path.name, 'csv', path.stem, 0.8, 0, [], 'pending')


registry.register('csv', CsvExtractor())
