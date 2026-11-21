from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import re

from ..schema_mapper import SchemaMapper
from ..validator import Validator
from ..logger import logger


class MdHandler:
    def __init__(self):
        self.schema_mapper = SchemaMapper()

    def _strip_md(self, text: str) -> str:
        # naive markdown stripping: remove code blocks and simple markup
        text = re.sub(r'```.*?```', ' ', text, flags=re.DOTALL)
        text = re.sub(r'`([^`]*)`', r"\1", text)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r"\1", text)
        text = re.sub(r'[#>*~-]+', ' ', text)
        return text

    def load(self, path: Path) -> Tuple[Optional[List[Dict[str, Any]]], Optional[Dict[str, str]], str]:
        try:
            raw = path.read_text(encoding='utf-8', errors='ignore')
            text = self._strip_md(raw).strip()
            if not text:
                return None, None, 'empty'

            row = {'title': path.stem, 'description': Validator.normalize_text(text)}
            header_map = self.schema_mapper.map_headers(['title', 'description'])
            return [self.schema_mapper.map_row(row, header_map)], header_map, 'md'
        except Exception as exc:
            logger.error('MdHandler failed to load %s: %s', path, exc)
            return None, None, 'error'
