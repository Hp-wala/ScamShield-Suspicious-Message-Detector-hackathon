from pathlib import Path
from typing import Any, Dict, List, Optional

from .logger import logger
from .metadata_store import MetadataStore
from .dataset_manager import DatasetManager


class KnowledgeIndex:
    def __init__(self, dataset_manager: DatasetManager, metadata_store: MetadataStore):
        self.dataset_manager = dataset_manager
        self.metadata_store = metadata_store

    def find_dataset_entries(self, dataset_name: str) -> List[Dict[str, Any]]:
        return self.dataset_manager.search_index(dataset_name)

    def search(self, query: str, subjects: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        query_lower = query.strip().lower()
        results: List[Dict[str, Any]] = []

        for dataset_name, entry in self.dataset_manager.registry.items():
            if subjects and entry['subject'] not in subjects:
                continue

            entries = self.find_dataset_entries(dataset_name)
            for item in entries:
                if self._matches(item, query_lower):
                    metadata = self.metadata_store.load_metadata(dataset_name)
                    results.append({
                        'dataset': dataset_name,
                        'subject': entry['subject'],
                        'title': item.get('title', ''),
                        'description': item.get('description', ''),
                        'category': item.get('category', ''),
                        'label': item.get('label', ''),
                        'score': self._score(item, query_lower),
                        'metadata': metadata,
                    })

        return sorted(results, key=lambda item: item['score'], reverse=True)

    def _matches(self, item: Dict[str, Any], query_lower: str) -> bool:
        for field in ['title', 'description', 'category', 'label']:
            if query_lower in str(item.get(field, '')).lower():
                return True
        return False

    def _score(self, item: Dict[str, Any], query_lower: str) -> float:
        score = 0.0
        title = str(item.get('title', '')).lower()
        description = str(item.get('description', '')).lower()
        if query_lower in title:
            score += 2.0
        if query_lower in description:
            score += 1.0
        return score
