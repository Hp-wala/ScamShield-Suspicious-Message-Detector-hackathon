from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.core.config_manager import ConfigManager
from src.core.dataset_manager import DatasetManager
from src.core.knowledge_graph import KnowledgeGraph
from src.core.logger import logger
from src.core.metadata_store import MetadataStore
from src.core.knowledge_index import KnowledgeIndex
from src.core.search_engine import SearchEngine
from src.core.update_manager import UpdateManager
from .extractor_registry import registry as extractor_registry
from .stages import (
    CleaningStage,
    EntityStage,
    MetadataStage,
    NormalizationStage,
    StructuringStage,
    TopicStage,
)


class KnowledgePipeline:
    def __init__(self, config: Optional[ConfigManager] = None, dataset_manager: Optional[DatasetManager] = None):
        self.config = config or ConfigManager()
        self.dataset_manager = dataset_manager or DatasetManager(self.config)
        self.metadata_store = MetadataStore(Path(self.config.get('cache_path')) / 'metadata')
        self.knowledge_graph = KnowledgeGraph(Path(self.config.get('cache_path')) / 'knowledge_graph.json')
        self.knowledge_index = KnowledgeIndex(self.dataset_manager, self.metadata_store)
        self.search_engine = SearchEngine(self.dataset_manager, self.knowledge_index)
        self.update_manager = UpdateManager(self)
        self.cleaner = CleaningStage()
        self.normalizer = NormalizationStage()
        self.entity_stage = EntityStage(self.knowledge_graph)
        self.topic_stage = TopicStage()
        self.structuring_stage = StructuringStage()
        self.metadata_stage = MetadataStage()

    def discover_modules(self) -> None:
        return

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
        for row in rows:
            for key in row.keys():
                if key not in keys:
                    keys.append(key)

        with out_file.open('w', encoding='utf-8', newline='') as handle:
            import csv

            writer = csv.DictWriter(handle, fieldnames=keys)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: row.get(k, '') for k in keys})

        logger.info('KnowledgePipeline wrote dataset %s', out_file)
        return out_file

    def process(self, path: Path, subject: Optional[str] = None) -> Tuple[bool, str]:
        path = Path(path)
        extractor = extractor_registry.get(path)
        if not extractor:
            return False, f'unsupported_format:{path.suffix}'
        if not extractor.validate(path):
            return False, 'invalid_path'

        rows, raw_metadata = extractor.extract(path)
        if rows is None:
            return False, raw_metadata.get('reason', 'failed_extraction')

        rows = self.cleaner.process(rows)
        if not rows:
            return False, 'empty_rows'

        rows = self.normalizer.process(rows)
        topic_info = self.topic_stage.detect(rows, path.name, self._infer_subject(subject, path))
        entities = self.entity_stage.extract(rows, f"{self._infer_subject(subject, path)}/{path.stem}")
        structured_rows = self.structuring_stage.structure(rows, str(path), topic_info['topic'], topic_info['confidence'])

        metadata = self.metadata_stage.create(
            str(path),
            path.name,
            path.suffix.lstrip('.'),
            topic_info['topic'],
            topic_info['confidence'],
            len(structured_rows),
            entities,
            'imported',
        )
        if isinstance(raw_metadata, dict):
            metadata.update(raw_metadata)

        subj = self._infer_subject(subject, path)
        name = path.stem
        self._write_dataset_csv(subj, name, structured_rows)

        dataset_key = f"{subj}/{name}"
        self.metadata_store.save_metadata(dataset_key, metadata)
        self.dataset_manager.refresh()
        self.update_manager.schedule_refresh()
        self.dataset_manager.load_dataset(dataset_key)
        self.knowledge_index = KnowledgeIndex(self.dataset_manager, self.metadata_store)
        self.search_engine = SearchEngine(self.dataset_manager, self.knowledge_index)
        return True, 'imported'
