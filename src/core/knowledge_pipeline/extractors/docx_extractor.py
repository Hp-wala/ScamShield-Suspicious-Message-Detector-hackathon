from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.core.knowledge_pipeline.base_extractor import BaseExtractor
from src.core.knowledge_pipeline.extractor_registry import registry
from src.core.knowledge_pipeline.stages.metadata_stage import MetadataStage
from src.core.schema_mapper import SchemaMapper
from src.core.validator import Validator

try:
    import docx
except ImportError:  # optional plugin support
    docx = None


class DocxExtractor(BaseExtractor):
    def validate(self, path: Path) -> bool:
        return path.suffix.lower() == '.docx' and path.exists()

    def extract(self, path: Path) -> Tuple[Optional[List[Dict[str, Any]]], Dict[str, Any]]:
        if docx is None:
            return None, {'status': 'missing_dependency', 'reason': 'python-docx not installed'}

        try:
            document = docx.Document(str(path))
            text_parts = [paragraph.text for paragraph in document.paragraphs if paragraph.text]
            text = ' '.join(text_parts).strip()
            if not text:
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
        return MetadataStage().create(str(path), path.name, 'docx', path.stem, 0.65, 0, [], 'pending')


registry.register('docx', DocxExtractor())
