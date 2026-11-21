from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .dataset_manager import DatasetManager
from .logger import logger


class SubjectModule(ABC):
    name: str
    subject: str

    def __init__(self, dataset_manager: DatasetManager, subject: str) -> None:
        self.dataset_manager = dataset_manager
        self.subject = subject
        self.name = subject

    @abstractmethod
    def initialize(self) -> None:
        ...

    @abstractmethod
    def list_datasets(self) -> List[str]:
        ...

    @abstractmethod
    def load_dataset(self, dataset_name: str) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    def train(self, dataset_name: str) -> Dict[str, Any]:
        ...


class GenericSubjectModule(SubjectModule):
    def __init__(self, dataset_manager: DatasetManager, subject: str) -> None:
        super().__init__(dataset_manager, subject)

    def initialize(self) -> None:
        for dataset_name in self.list_datasets():
            self.load_dataset(dataset_name)

    def list_datasets(self) -> List[str]:
        return [
            dataset_name
            for dataset_name, entry in self.dataset_manager.registry.items()
            if entry.get('subject') == self.subject
        ]

    def load_dataset(self, dataset_name: str) -> List[Dict[str, Any]]:
        return self.dataset_manager.load_dataset(dataset_name)

    def train(self, dataset_name: str) -> Dict[str, Any]:
        rows = self.load_dataset(dataset_name)
        if not rows:
            logger.warning('No rows available for training subject=%s dataset=%s', self.subject, dataset_name)
            return {}

        try:
            from ..training.generic_trainer import GenericTrainer

            trainer = GenericTrainer(self.dataset_manager.config_manager, self.subject)
            report = trainer.retrain(rows)
            return report or {}
        except Exception as exc:
            logger.error('Training failed for subject=%s dataset=%s: %s', self.subject, dataset_name, exc)
            return {}
