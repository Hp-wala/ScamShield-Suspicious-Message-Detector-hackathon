import os
from typing import Any, Dict, List, Optional

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    joblib = None
    JOBLIB_AVAILABLE = False

from src.core.config_manager import ConfigManager
from src.core.logger import logger
from src.core.validator import Validator
from src.preprocessing.spam_preprocessor import SpamPreprocessor


class SpamDetector:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.model_dir = self.config_manager.get('model_path')
        self.model_file = os.path.join(self.model_dir, self.config_manager.get('default_model_name'))
        self.vectorizer = None
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        if not os.path.exists(self.model_file):
            logger.warning('No model found at %s, fallback to rule-based detection.', self.model_file)
            return

        if not JOBLIB_AVAILABLE:
            logger.warning('joblib is unavailable; using rule-based detection only.')
            return

        try:
            data = joblib.load(self.model_file)
            self.vectorizer = data.get('vectorizer')
            self.model = data.get('model')
            logger.info('Loaded spam model from %s', self.model_file)
        except Exception as exc:
            logger.error('Failed to load spam model: %s', exc)
            self.vectorizer = None
            self.model = None

    def _rule_based_detect(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        text = SpamPreprocessor.extract_text_fields(email_data)
        normalized = SpamPreprocessor.clean_text(text)
        score = 0
        reasons: List[str] = []

        if 'free' in normalized:
            score += 10
            reasons.append('Contains the word free')

        if SpamPreprocessor.extract_urls(normalized) > 0:
            score += 15
            reasons.append('Contains URL')

        if 'urgent' in normalized or 'click here' in normalized:
            score += 12
            reasons.append('Suspicious urgency or CTA')

        if 'verify your account' in normalized or 'update your information' in normalized:
            score += 10
            reasons.append('Contains verification or update request')

        label = 'spam' if score >= 30 else 'ham'
        return {'label': label, 'score': min(score / 100.0, 1.0), 'reasons': reasons}

    def predict_with_details(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        if self.model is None or self.vectorizer is None:
            return self._rule_based_detect(email_data)

        try:
            text = SpamPreprocessor.extract_text_fields(email_data)
            text = SpamPreprocessor.clean_text(text)
            features = self.vectorizer.transform([text])
            prediction = self.model.predict(features)[0]
            score = 0.0
            if hasattr(self.model, 'predict_proba'):
                score = float(self.model.predict_proba(features)[0][1])

            label = 'spam' if int(prediction) == 1 else 'ham'
            reasons = ['Model-based prediction']
            return {'label': label, 'score': score, 'reasons': reasons}
        except Exception as exc:
            logger.error('Prediction failed: %s', exc)
            return self._rule_based_detect(email_data)

    def predict(self, email_data: Dict[str, Any]) -> str:
        return self.predict_with_details(email_data)['label']

    def predict_proba(self, email_data: Dict[str, Any]) -> float:
        try:
            result = self.predict_with_details(email_data)
            return float(result.get('score', 0.0))
        except Exception as exc:
            logger.error('Probability prediction failed: %s', exc)
            return self._rule_based_detect(email_data)['score']

    def score(self, email_dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        from src.evaluation.spam_metrics import MetricsCalculator

        y_true = []
        y_pred = []
        y_prob = []

        for row in email_dataset:
            label = row.get('label')
            if str(label).strip().lower() not in {'spam', '1', 'true', 'yes', 'ham', '0', 'false', 'no'}:
                continue
            y_true.append(1 if str(label).strip().lower() in {'spam', '1', 'true', 'yes'} else 0)
            y_pred.append(1 if self.predict(row) == 'spam' else 0)
            y_prob.append(self.predict_proba(row))

        if not y_true:
            logger.warning('No labeled rows found for scoring.')
            return {}

        metrics = MetricsCalculator.calculate(y_true, y_pred, y_prob)
        report = MetricsCalculator.to_dict(metrics)
        logger.info('Scored dataset: %s', report)
        return report

    def save_model(self) -> bool:
        try:
            if self.model is None or self.vectorizer is None:
                logger.warning('No model available to save.')
                return False
            os.makedirs(self.model_dir, exist_ok=True)
            joblib.dump({'vectorizer': self.vectorizer, 'model': self.model}, self.model_file)
            logger.info('Saved spam model to %s', self.model_file)
            return True
        except Exception as exc:
            logger.error('Failed to save spam model: %s', exc)
            return False

    def load_model(self) -> bool:
        try:
            self._load_model()
            return self.model is not None and self.vectorizer is not None
        except Exception as exc:
            logger.error('Failed to reload spam model: %s', exc)
            return False

    def retrain(self, rows: List[Dict[str, Any]], model_type: str = 'logistic') -> Optional[Dict[str, Any]]:
        from src.training.spam_trainer import SpamTrainer

        trainer = SpamTrainer(self.config_manager)
        report = trainer.retrain(rows, model_type=model_type)
        if report:
            self._load_model()
        return report
