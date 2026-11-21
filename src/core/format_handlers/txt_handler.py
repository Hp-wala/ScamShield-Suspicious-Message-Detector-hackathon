from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..schema_mapper import SchemaMapper
from ..validator import Validator
from ..logger import logger


class TxtHandler:
    def __init__(self):
        self.schema_mapper = SchemaMapper()

    def load(self, path: Path) -> Tuple[Optional[List[Dict[str, Any]]], Optional[Dict[str, str]], str]:
        try:
            text = path.read_text(encoding='utf-8', errors='ignore').strip()
            if not text:
                return None, None, 'empty'

            # single-row dataset with title=filename, description=text
            row = {'title': path.stem, 'description': Validator.normalize_text(text)}
            header_map = self.schema_mapper.map_headers(['title', 'description'])
            return [self.schema_mapper.map_row(row, header_map)], header_map, 'txt'
        except Exception as exc:
            logger.error('TxtHandler failed to load %s: %s', path, exc)
            return None, None, 'error'
