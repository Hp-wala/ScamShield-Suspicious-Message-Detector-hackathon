import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .logger import logger


class DatasetIndexer:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def index(self, dataset_name: str, rows: Iterable[Dict[str, Any]]) -> bool:
        try:
            index_file = self.cache_dir / f'{dataset_name}.idx.json'
            index_file.parent.mkdir(parents=True, exist_ok=True)
            minimal_index = [self._row_index(row) for row in rows]
            with index_file.open('w', encoding='utf-8') as handle:
                json.dump(minimal_index, handle, ensure_ascii=False, indent=2)
            logger.info('Indexed dataset: %s entries=%d', dataset_name, len(minimal_index))
            return True
        except Exception as exc:
            logger.error('Failed to index dataset %s: %s', dataset_name, exc)
            return False

    def _row_index(self, row: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'id': row.get('id', ''),
            'title': row.get('title', ''),
            'description': row.get('description', ''),
            'category': row.get('category', ''),
            'label': row.get('label', ''),
            'value': row.get('value', ''),
        }
