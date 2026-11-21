import re
from typing import Dict, Iterable, List, Optional, Tuple

from .validator import Validator
from .memory_store import MemoryStore
from .config_manager import ConfigManager


STANDARD_FIELD_ALIASES: Dict[str, List[str]] = {
    'id': ['id', 'uid', 'uuid', 'record id', 'record_id', 'identifier'],
    'title': [
        'title', 'name', 'subject', 'question', 'term', 'topic', 'medicine name',
        'drug', 'protocol', 'command', 'function', 'label name', 'item'
    ],
    'description': [
        'description', 'body', 'details', 'notes', 'answer', 'definition',
        'summary', 'explanation', 'instructions', 'context'
    ],
    'category': [
        'category', 'type', 'class', 'group', 'topic', 'domain', 'section',
        'grouping'
    ],
    'label': [
        'label', 'tag', 'status', 'result', 'class', 'outcome', 'category'
    ],
    'value': ['value', 'amount', 'dose', 'dosage', 'score', 'rating'],
}

FALLBACK_FIELDS: List[str] = ['title', 'description']


def normalize_header(header: str) -> str:
    text = header.strip().lower()
    text = re.sub(r'[\s_\-]+', ' ', text)
    text = re.sub(r'[^a-z0-9 ]+', '', text)
    return text


class SchemaMapper:
    def __init__(self, memory_store: Optional[MemoryStore] = None) -> None:
        self.alias_map = self._build_alias_map()
        # allow injection of a MemoryStore for testing or custom stores
        if memory_store is not None:
            self._memory = memory_store
        else:
            try:
                cfg = ConfigManager()
                mem_file = cfg.get('cache_path')
                from pathlib import Path

                self._memory = MemoryStore(Path(mem_file) / 'memory_store.json') if mem_file else None
            except Exception:
                self._memory = None

        # approved mappings cached by normalized header keyset
        self.approved_mappings: Dict[frozenset, Dict[str, str]] = {}
        if self._memory:
            try:
                for item in self._memory.list_schema_approvals():
                    mapping = item.get('mapping')
                    if mapping and isinstance(mapping, dict):
                        norm_keys = frozenset(normalize_header(k) for k in mapping.keys())
                        self.approved_mappings[norm_keys] = mapping
            except Exception:
                pass

    def _build_alias_map(self) -> Dict[str, str]:
        alias_map: Dict[str, str] = {}
        for standard, aliases in STANDARD_FIELD_ALIASES.items():
            for alias in aliases:
                alias_map[normalize_header(alias)] = standard
        return alias_map

    def map_headers(self, headers: Iterable[str]) -> Optional[Dict[str, str]]:
        # Backward compatible API: try to reuse approved mappings first.
        headers_list = [h for h in headers if isinstance(h, str) and h]
        normalized_keys = [normalize_header(h) for h in headers_list]
        keyset = frozenset(normalized_keys)
        if keyset in self.approved_mappings:
            return self.approved_mappings[keyset]

        header_map, confidence = self.map_headers_with_confidence(headers_list)
        # keep legacy behaviour: if no fallback fields present, return None
        if header_map is None:
            return None
        return header_map

    def map_headers_with_confidence(self, headers: Iterable[str]) -> Tuple[Optional[Dict[str, str]], float]:
        header_map: Dict[str, str] = {}
        mapped_targets = set()
        total = 0

        for header in headers:
            if not header or not isinstance(header, str):
                continue
            total += 1

            normalized = normalize_header(header)
            target = self.alias_map.get(normalized)
            if target:
                header_map[header] = target
                mapped_targets.add(target)
                continue

            if 'id' in normalized and normalized not in {'idea', 'audio'}:
                header_map[header] = 'id'
                mapped_targets.add('id')
                continue

            header_map[header] = 'metadata'

        confidence = (len(mapped_targets) / total) if total > 0 else 0.0

        if not any(field in mapped_targets for field in FALLBACK_FIELDS):
            return None, confidence

        return header_map, confidence

    def save_approved_mapping(self, dataset_name: str, mapping: Dict[str, str]) -> None:
        try:
            if not self._memory:
                return
            self._memory.approve_schema_mapping(dataset_name, mapping)
            norm_keys = frozenset(normalize_header(k) for k in mapping.keys())
            self.approved_mappings[norm_keys] = mapping
        except Exception:
            pass

    def map_row(self, row: Dict[str, any], header_map: Dict[str, str]) -> Dict[str, str]:
        mapped: Dict[str, str] = {
            'id': '',
            'title': '',
            'description': '',
            'category': '',
            'label': '',
            'value': '',
            'metadata': {},
        }

        for key, raw_value in row.items():
            destination = header_map.get(key, 'metadata')
            value = Validator.normalize_text(raw_value)
            if not value:
                continue

            # Preserve original raw fields alongside the normalized schema.
            mapped[key] = value

            if destination in mapped and destination != 'metadata':
                if not mapped[destination]:
                    mapped[destination] = value
                elif destination == 'title' and not mapped['description']:
                    mapped['description'] = value
                elif destination == 'description' and not mapped['category']:
                    mapped['category'] = value
                else:
                    mapped['metadata'][key] = value
            else:
                mapped['metadata'][key] = value

        return mapped

    def is_confident(self, mapping: Optional[Dict[str, str]]) -> bool:
        return mapping is not None
