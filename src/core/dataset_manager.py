import threading
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .config_manager import ConfigManager
from .dataset_loader import DatasetLoader
from .indexer import DatasetIndexer
from .logger import logger


class DatasetManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.datasets_path: Path = Path(self.config_manager.get('datasets_path'))
        self.supported_extensions = self.config_manager.get('supported_dataset_extensions', ('.csv', '.json'))
        self.loader = DatasetLoader()
        self.indexer = DatasetIndexer(Path(self.config_manager.get('cache_path')) / 'datasets')
        self.registry: Dict[str, Dict[str, Any]] = {}
        self._dataset_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._cache_lock = threading.RLock()
        self.discover_datasets()

    def discover_datasets(self) -> None:
        self.datasets_path.mkdir(parents=True, exist_ok=True)
        self.registry.clear()

        for path in sorted(self.datasets_path.rglob('*')):
            if not path.is_file():
                continue
            if path.suffix.lower() not in self.supported_extensions:
                logger.info('Skipping unsupported dataset format: %s', path)
                continue

            dataset_key = self._dataset_key(path)
            subject = self._subject_for_path(path)
            entry = {
                'path': path,
                'subject': subject,
                'format': path.suffix.lower().lstrip('.'),
                'status': 'discovered',
                'header_map': None,
            }
            self.registry[dataset_key] = entry
            logger.info('Discovered dataset: %s subject=%s path=%s', dataset_key, subject, path)

        if not self.registry:
            logger.warning('No datasets found under %s', self.datasets_path)

    def _dataset_key(self, path: Path) -> str:
        relative = path.relative_to(self.datasets_path).with_suffix('')
        return relative.as_posix()

    def _subject_for_path(self, path: Path) -> str:
        parts = path.relative_to(self.datasets_path).parts
        return parts[0] if len(parts) > 1 else 'root'

    def list_subjects(self) -> List[str]:
        return sorted({entry['subject'] for entry in self.registry.values()})

    def list_datasets(self) -> List[str]:
        return sorted(self.registry.keys())

    def get_dataset_path(self, name: str) -> Optional[Path]:
        entry = self.registry.get(name)
        return entry['path'] if entry else None

    def get_dataset_entry(self, name: str) -> Optional[Dict[str, Any]]:
        return self.registry.get(name)

    def load_dataset(self, name: str, confirm_schema: bool = False) -> List[Dict[str, Any]]:
        if name not in self.registry:
            logger.warning('Dataset not found: %s', name)
            return []

        with self._cache_lock:
            if name in self._dataset_cache:
                logger.info('Returning cached dataset: %s', name)
                return [row.copy() for row in self._dataset_cache[name]]

        entry = self.registry[name]
        rows, header_map, status = self.loader.load(entry['path'])
        entry['status'] = status
        entry['header_map'] = header_map

        if status != 'csv' and status != 'json':
            logger.warning('Dataset %s could not be loaded: %s', name, status)
            return []

        if rows is None:
            logger.warning('Dataset %s returned no rows due to status: %s', name, status)
            return []

        if confirm_schema and header_map is None:
            logger.warning('Schema could not be confidently mapped for dataset %s', name)
            return []

        if not rows:
            logger.warning('Dataset %s is empty after import', name)
            return []

        self.indexer.index(name, rows)

        with self._cache_lock:
            self._dataset_cache[name] = [row.copy() for row in rows]

        return [row.copy() for row in rows]

    def refresh(self) -> None:
        logger.info('Refreshing dataset registry and cache')
        with self._cache_lock:
            self._dataset_cache.clear()
        self.discover_datasets()

    def search_index(self, name: str) -> List[Dict[str, Any]]:
        entry = self.registry.get(name)
        if not entry:
            logger.warning('Dataset not found for index search: %s', name)
            return []

        index_file = Path(self.config_manager.get('cache_path')) / 'datasets' / f'{name}.idx.json'
        if not index_file.exists():
            logger.warning('Index file missing for dataset: %s', name)
            return []

        try:
            with index_file.open('r', encoding='utf-8') as handle:
                return __import__('json').load(handle)
        except Exception as exc:
            logger.error('Failed to read index for %s: %s', name, exc)
            return []
