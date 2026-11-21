import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .logger import logger
from .schema_mapper import SchemaMapper
from .validator import Validator
from .format_handlers import registry as format_registry


class DatasetLoader:
    def __init__(self) -> None:
        self.schema_mapper = SchemaMapper()

    def detect_format(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix == '.csv':
            return 'csv'
        if suffix == '.json':
            return 'json'
        return 'unknown'

    def load(self, path: Path) -> Tuple[Optional[List[Dict[str, Any]]], Optional[Dict[str, str]], str]:
        # Prefer handler registry if available (pluggable handlers)
        try:
            rows, header_map, status = format_registry.load(path)
            if status != 'unsupported':
                return rows, header_map, status
        except Exception:
            # registry errors should not break fallback behaviour
            logger.exception('Format registry failed for %s', path)

        # Fallback to legacy detection for backward compatibility
        format_name = self.detect_format(path)
        if format_name == 'csv':
            return self._load_csv(path)
        if format_name == 'json':
            return self._load_json(path)
        logger.warning('Unsupported dataset format for %s', path)
        return None, None, 'unsupported'

    def _load_csv(self, path: Path) -> Tuple[Optional[List[Dict[str, Any]]], Optional[Dict[str, str]], str]:
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
                    cleaned = self._clean_row(raw_row)
                    rows.append(self.schema_mapper.map_row(cleaned, header_map))

            logger.info('Loaded CSV dataset %s rows=%d', path.name, len(rows))
            return rows, header_map, 'csv'
        except Exception as exc:
            logger.error('Failed to load CSV %s: %s', path, exc)
            return None, None, 'error'

    def _load_json(self, path: Path) -> Tuple[Optional[List[Dict[str, Any]]], Optional[Dict[str, str]], str]:
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
                cleaned = self._clean_row(item)
                rows.append(self.schema_mapper.map_row(cleaned, header_map))

            logger.info('Loaded JSON dataset %s rows=%d', path.name, len(rows))
            return rows, header_map, 'json'
        except Exception as exc:
            logger.error('Failed to load JSON %s: %s', path, exc)
            return None, None, 'error'

    def _clean_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        cleaned: Dict[str, Any] = {}
        for key, value in row.items():
            if Validator.is_valid_string(value):
                cleaned[key] = Validator.normalize_text(value)
            else:
                cleaned[key] = ''
        return cleaned
