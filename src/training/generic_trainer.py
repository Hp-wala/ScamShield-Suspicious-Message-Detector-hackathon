import os
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    joblib = None
    JOBLIB_AVAILABLE = False

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from ..core.config_manager import ConfigManager
from ..core.logger import logger
from ..core.validator import Validator
from ..evaluation.spam_metrics import MetricsCalculator


class GenericTrainer:
    def __init__(self, config_manager: ConfigManager, subject_name: str):
        self.config_manager = config_manager
        self.subject_name = subject_name
        self.model_dir = Path(self.config_manager.get('model_path')) / subject_name
        self.model_file = self.model_dir / self.config_manager.get('default_model_name')
        self.vectorizer = TfidfVectorizer(max_features=5000)
        self.model = LogisticRegression(max_iter=1000)

    def _safe_dataset(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [row for row in rows if Validator.is_valid_string(row.get('title')) or Validator.is_valid_string(row.get('description'))]

    def preprocess(self, rows: List[Dict[str, Any]]) -> tuple[List[str], List[int]]:
        rows = self._safe_dataset(rows)
        texts: List[str] = []
        labels: List[int] = []

        for row in rows:
            text = ' '.join(filter(None, [row.get('title', ''), row.get('description', '')]))
            if not text:
                continue
            texts.append(text)
            label = row.get('label', '').strip().lower()
            labels.append(1 if label in {'spam', '1', 'true', 'yes'} else 0)

        return texts, labels

    def train(self, rows: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        try:
            texts, labels = self.preprocess(rows)
            if len(texts) < 2 or len(set(labels)) < 2:
                logger.warning('Not enough labeled data to train model for %s', self.subject_name)
                return None

            features = self.vectorizer.fit_transform(texts)
            X_train, X_val, y_train, y_val = train_test_split(
                features, labels, test_size=0.2, random_state=42, stratify=labels
            )
            self.model.fit(X_train, y_train)

            y_pred = self.model.predict(X_val)
            y_prob = self.model.predict_proba(X_val)[:, 1] if hasattr(self.model, 'predict_proba') else None
            metrics = MetricsCalculator.calculate(y_val, y_pred, y_prob)
            report = MetricsCalculator.to_dict(metrics)

            logger.info('Training complete for %s: %s', self.subject_name, report)
            return report
        except Exception as exc:
            logger.error('Training failed for %s: %s', self.subject_name, exc)
            return None

    def save_model(self) -> bool:
        if not JOBLIB_AVAILABLE:
            logger.warning('joblib unavailable; cannot save model for %s', self.subject_name)
            return False

        try:
            self.model_dir.mkdir(parents=True, exist_ok=True)
            joblib.dump({'vectorizer': self.vectorizer, 'model': self.model}, self.model_file)
            logger.info('Saved model for %s to %s', self.subject_name, self.model_file)
            return True
        except Exception as exc:
            logger.error('Failed to save model for %s: %s', self.subject_name, exc)
            return False

    def load_model(self) -> bool:
        if not self.model_file.exists() or not JOBLIB_AVAILABLE:
            logger.warning('Model file missing or joblib unavailable for %s', self.subject_name)
            return False

        try:
            data = joblib.load(self.model_file)
            self.vectorizer = data.get('vectorizer')
            self.model = data.get('model')
            logger.info('Loaded model for %s', self.subject_name)
            return True
        except Exception as exc:
            logger.error('Failed to load model for %s: %s', self.subject_name, exc)
            return False

    def retrain(self, rows: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        report = self.train(rows)
        if report is None:
            return None
        return report if self.save_model() else None
