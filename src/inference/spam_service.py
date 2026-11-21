from datetime import datetime
from typing import Any, Dict, List, Optional

from ..core.config_manager import ConfigManager
from ..core.dataset_manager import DatasetManager
from ..core.logger import logger
from .spam_detector import SpamDetector
from ..training.spam_feedback import SpamFeedback
from ..training.spam_trainer import SpamTrainer


class SpamService:
    def __init__(self, config: Optional[ConfigManager] = None):
        self.config_manager = config or ConfigManager()
        self.config_manager.ensure_paths()
        self.dataset_manager = DatasetManager(self.config_manager)
        self.detector = SpamDetector(self.config_manager)
        self.trainer = SpamTrainer(self.config_manager)
        self.feedback = SpamFeedback(self.config_manager.get('feedback_file'))

    def list_datasets(self) -> List[str]:
        return self.dataset_manager.list_datasets()

    def train(self, dataset_name: str, model_type: str = 'logistic') -> Dict[str, Any]:
        rows = self.dataset_manager.load_dataset(dataset_name)
        if not rows:
            logger.warning('Training skipped because dataset is empty or missing: %s', dataset_name)
            return {}

        report = self.trainer.train(rows, model_type=model_type)
        if report is None:
            return {}

        if self.trainer.save_model():
            self.detector.load_model()
        return report

    def predict(self, email_data: Dict[str, Any]) -> str:
        try:
            return self.detector.predict(email_data)
        except Exception as exc:
            logger.error('Spam prediction failed: %s', exc)
            return 'ham'

    def predict_proba(self, email_data: Dict[str, Any]) -> float:
        try:
            return self.detector.predict_proba(email_data)
        except Exception as exc:
            logger.error('Spam probability failed: %s', exc)
            return 0.0

    def score(self, dataset_name: str) -> Dict[str, Any]:
        rows = self.dataset_manager.load_dataset(dataset_name)
        if not rows:
            logger.warning('Scoring skipped because dataset is empty or missing: %s', dataset_name)
            return {}
        return self.detector.score(rows)

    def save_model(self) -> bool:
        return self.detector.save_model()

    def load_model(self) -> bool:
        return self.detector.load_model()

    def retrain(self, dataset_name: str, model_type: str = 'logistic') -> Dict[str, Any]:
        rows = self.dataset_manager.load_dataset(dataset_name)
        if not rows:
            logger.warning('Retraining skipped because dataset is empty or missing: %s', dataset_name)
            return {}
        report = self.detector.retrain(rows, model_type=model_type)
        return report or {}

    def submit_feedback(self, email_data: Dict[str, Any], label: str) -> bool:
        try:
            return self.feedback.store_feedback(email_data, label, datetime.utcnow().isoformat())
        except Exception as exc:
            logger.error('Failed to submit feedback: %s', exc)
            return False
