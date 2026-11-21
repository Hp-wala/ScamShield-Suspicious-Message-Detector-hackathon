import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..schema_mapper import SchemaMapper
from ..validator import Validator
from ..logger import logger


class JsonHandler:
    def __init__(self):
        self.schema_mapper = SchemaMapper()

    def load(self, path: Path) -> Tuple[Optional[List[Dict[str, Any]]], Optional[Dict[str, str]], str]:
        try:
            with path.open('r', encoding='utf-8') as handle:
                payload = json.load(handle)

            if isinstance(payload, dict):
                payload = [payload]
            if not isinstance(payload, list):
                logger.warning('JSON dataset is not a list or object: %s', path)
                return None, None, 'invalid'

            rows: List[Dict[str, Any]] = []
            header_map = None
            for item in payload:
                if not isinstance(item, dict):
                    continue
                if header_map is None:
                    header_map = self.schema_mapper.map_headers(item.keys())
                    if header_map is None:
                        logger.warning('Unable to map JSON headers for dataset: %s', path)
                        return None, None, 'unmapped'
                cleaned = {}
                for key, value in item.items():
                    if Validator.is_valid_string(value):
                        cleaned[key] = Validator.normalize_text(value)
                    else:
                        cleaned[key] = ''
                rows.append(self.schema_mapper.map_row(cleaned, header_map))

            logger.info('JSON handler loaded %s rows=%d', path.name, len(rows))
            return rows, header_map, 'json'
        except Exception as exc:
            logger.error('JSON handler failed to load %s: %s', path, exc)
            return None, None, 'error'
