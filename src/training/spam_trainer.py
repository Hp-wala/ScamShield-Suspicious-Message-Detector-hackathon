import os
from typing import Any, Dict, List, Optional

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    joblib = None
    JOBLIB_AVAILABLE = False

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split

from src.core.config_manager import ConfigManager
from src.core.logger import logger
from src.core.validator import Validator
from src.evaluation.spam_metrics import MetricsCalculator
from src.preprocessing.spam_preprocessor import SpamPreprocessor


class SpamTrainer:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.model_dir = self.config_manager.get('model_path')
        self.model_file = os.path.join(self.model_dir, self.config_manager.get('default_model_name'))
        self.vectorizer = TfidfVectorizer(max_features=5000)
        self.model = LogisticRegression(max_iter=1000)

    def _safe_dataset(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        valid_rows = []
        for row in rows:
            if Validator.is_valid_string(row.get('subject')) or Validator.is_valid_string(row.get('body')):
                valid_rows.append(row)
        return valid_rows

    def preprocess(self, rows: List[Dict[str, Any]]) -> tuple[List[str], List[int]]:
        rows = self._safe_dataset(rows)
        texts = []
        labels = []

        for row in rows:
            text = SpamPreprocessor.extract_text_fields(row)
            if not text:
                continue
            text = SpamPreprocessor.clean_text(text)
            texts.append(text)

            label = row.get('label')
            if str(label).strip().lower() in {'spam', '1', 'true', 'yes'}:
                labels.append(1)
            else:
                labels.append(0)

        return texts, labels

    def train(self, rows: List[Dict[str, Any]], model_type: str = 'logistic') -> Optional[Dict[str, Any]]:
        try:
            texts, labels = self.preprocess(rows)
            if not texts or not labels:
                logger.warning('No valid training samples found.')
                return None

            if len(texts) < 2 or len(labels) < 2:
                logger.warning('Not enough training data to train model.')
                return None

            if len(set(labels)) < 2:
                logger.warning('Training data does not contain both spam and ham labels.')
                return None

            if model_type == 'count':
                self.vectorizer = CountVectorizer(max_features=5000)
            else:
                self.vectorizer = TfidfVectorizer(max_features=5000)

            features = self.vectorizer.fit_transform(texts)

            if model_type == 'random_forest':
                self.model = RandomForestClassifier(n_estimators=100)
            elif model_type == 'gradient_boosting':
                self.model = GradientBoostingClassifier(n_estimators=100)
            else:
                self.model = LogisticRegression(max_iter=1000)

            X_train, X_val, y_train, y_val = train_test_split(
                features, labels, test_size=0.2, random_state=42, stratify=labels
            )
            self.model.fit(X_train, y_train)

            y_pred = self.model.predict(X_val)
            y_prob = self.model.predict_proba(X_val)[:, 1] if hasattr(self.model, 'predict_proba') else None
            metrics = MetricsCalculator.calculate(y_val, y_pred, y_prob)
            report = MetricsCalculator.to_dict(metrics)

            logger.info('Training complete: %s', report)
            return report
        except Exception as exc:
            logger.error('Failed to train model: %s', exc)
            return None

    def save_model(self) -> bool:
        if not JOBLIB_AVAILABLE:
            logger.warning('joblib is unavailable; cannot save model.')
            return False

        try:
            os.makedirs(self.model_dir, exist_ok=True)
            joblib.dump({'vectorizer': self.vectorizer, 'model': self.model}, self.model_file)
            logger.info('Saved model to %s', self.model_file)
            return True
        except Exception as exc:
            logger.error('Failed to save model: %s', exc)
            return False

    def load_model(self) -> bool:
        try:
            if not os.path.exists(self.model_file):
                logger.warning('Model file not found: %s', self.model_file)
                return False
            data = joblib.load(self.model_file)
            self.vectorizer = data['vectorizer']
            self.model = data['model']
            logger.info('Loaded model from %s', self.model_file)
            return True
        except Exception as exc:
            logger.error('Failed to load model: %s', exc)
            return False

    def retrain(self, rows: List[Dict[str, Any]], model_type: str = 'logistic') -> Optional[Dict[str, Any]]:
        report = self.train(rows, model_type=model_type)
        if report is None:
            logger.warning('Retraining returned no report.')
            return None
        saved = self.save_model()
        return report if saved else None
