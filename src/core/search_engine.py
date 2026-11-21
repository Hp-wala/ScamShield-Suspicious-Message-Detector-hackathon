from typing import Any, Dict, List, Optional

from .dataset_manager import DatasetManager
from .knowledge_index import KnowledgeIndex


class SearchEngine:
    def __init__(self, dataset_manager: DatasetManager, knowledge_index: KnowledgeIndex):
        self.dataset_manager = dataset_manager
        self.knowledge_index = knowledge_index

    def search(self, query: str, subjects: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        return self.knowledge_index.search(query, subjects)

    def search_subject(self, query: str, subject: str) -> List[Dict[str, Any]]:
        datasets = [name for name, entry in self.dataset_manager.registry.items() if entry['subject'] == subject]
        return self.search(query, datasets)
