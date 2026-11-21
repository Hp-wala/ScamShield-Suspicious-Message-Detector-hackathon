import csv
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..schema_mapper import SchemaMapper
from ..validator import Validator
from ..logger import logger


class CsvHandler:
    def __init__(self):
        self.schema_mapper = SchemaMapper()

    def load(self, path: Path) -> Tuple[Optional[List[Dict[str, Any]]], Optional[Dict[str, str]], str]:
        rows: List[Dict[str, Any]] = []
        try:
            with path.open('r', encoding='utf-8', errors='ignore') as handle:
                reader = csv.DictReader(handle)
                if not reader.fieldnames:
                    logger.warning('CSV has no headers: %s', path)
                    return None, None, 'invalid'

                header_map = self.schema_mapper.map_headers(reader.fieldnames)
                if header_map is None:
                    logger.warning('Unable to map headers for dataset: %s', path)
                    return None, None, 'unmapped'

                for raw_row in reader:
                    cleaned = {}
                    for key, value in raw_row.items():
                        if Validator.is_valid_string(value):
                            cleaned[key] = Validator.normalize_text(value)
                        else:
                            cleaned[key] = ''
                    rows.append(self.schema_mapper.map_row(cleaned, header_map))

            logger.info('CSV handler loaded %s rows=%d', path.name, len(rows))
            return rows, header_map, 'csv'
        except Exception as exc:
            logger.error('CSV handler failed to load %s: %s', path, exc)
            return None, None, 'error'
