from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import csv

from .config_manager import ConfigManager
from .dataset_manager import DatasetManager
from .format_handlers import registry as format_registry
from .knowledge_pipeline import KnowledgePipeline, registry as extractor_registry
from .memory_store import MemoryStore
from .logger import logger


class KnowledgeFactory:
    """Processes arbitrary files and converts them into structured datasets.

    - Uses the new knowledge pipeline for supported extractors.
    - Falls back to the legacy format handler registry for additional formats.
    - Writes CSV files into the configured datasets path and refreshes the dataset registry.
    """

    def __init__(self, config: Optional[ConfigManager] = None, dataset_manager: Optional[DatasetManager] = None):
        self.config = config or ConfigManager()
        self.dataset_manager = dataset_manager or DatasetManager(self.config)
        self.memory = MemoryStore(Path(self.config.get('cache_path')) / 'memory_store.json')
        self.pipeline = KnowledgePipeline(self.config, self.dataset_manager)

    def _infer_subject(self, target_subject: Optional[str], path: Path) -> str:
        if target_subject:
            return target_subject
        return path.stem

    def _write_dataset_csv(self, subject: str, name: str, rows: List[Dict[str, Any]]) -> Path:
        datasets_root: Path = Path(self.config.get('datasets_path'))
        target_dir = datasets_root / subject
        target_dir.mkdir(parents=True, exist_ok=True)
        out_file = target_dir / f"{name}.csv"

        keys: List[str] = []
        for r in rows:
            for k in r.keys():
                if k not in keys:
                    keys.append(k)

        try:
            with out_file.open('w', encoding='utf-8', newline='') as handle:
                writer = csv.DictWriter(handle, fieldnames=keys)
                writer.writeheader()
                for r in rows:
                    writer.writerow({k: r.get(k, '') for k in keys})
            logger.info('KnowledgeFactory wrote dataset %s', out_file)
            return out_file
        except Exception as exc:
            logger.error('Failed to write dataset csv %s: %s', out_file, exc)
            raise

    def process(self, path: Path, subject: Optional[str] = None) -> Tuple[bool, str]:
        path = Path(path)
        if not path.exists():
            return False, 'file_not_found'

        if extractor_registry.get(path):
            return self.pipeline.process(path, subject)

        rows, header_map, status = format_registry.load(path)
        if status in ('unsupported', None):
            return False, f'unsupported_format:{path.suffix}'
        if rows is None:
            return False, f'failed_load:{status}'

        subj = self._infer_subject(subject, path)
        name = path.stem

        try:
            self._write_dataset_csv(subj, name, rows)
            try:
                if header_map and len(header_map) >= 1:
                    self.memory.approve_schema_mapping(f"{subj}/{name}", header_map)
            except Exception:
                logger.debug('Could not persist schema approval')

            try:
                self.dataset_manager.refresh()
            except Exception:
                logger.exception('Failed to refresh dataset manager after import')

            return True, 'imported'
        except Exception as exc:
            logger.error('KnowledgeFactory failed to import %s: %s', path, exc)
            return False, f'error:{exc}'
