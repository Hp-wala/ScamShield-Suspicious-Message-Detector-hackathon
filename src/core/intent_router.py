from typing import Dict, List

from .dataset_manager import DatasetManager
from .module_registry import ModuleRegistry


class IntentRouter:
    def __init__(self, dataset_manager: DatasetManager, module_registry: ModuleRegistry):
        self.dataset_manager = dataset_manager
        self.module_registry = module_registry

    def route(self, query: str) -> List[str]:
        normalized = query.strip().lower()
        candidates: Dict[str, int] = {}

        for subject in self.dataset_manager.list_subjects():
            if subject.lower() in normalized:
                candidates[subject] = candidates.get(subject, 0) + 10

        for name in self.module_registry.list_plugins():
            if name.lower() in normalized:
                candidates[name] = candidates.get(name, 0) + 8

        words = set(normalized.split())
        for subject in self.dataset_manager.list_subjects():
            score = sum(1 for word in words if word in subject.lower())
            if score:
                candidates[subject] = candidates.get(subject, 0) + score

        if candidates:
            ranked = sorted(candidates.items(), key=lambda item: item[1], reverse=True)
            return [subject for subject, _ in ranked]

        return self.dataset_manager.list_subjects()
