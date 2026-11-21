from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    joblib = None
    JOBLIB_AVAILABLE = False

from ..core.config_manager import ConfigManager
from ..core.logger import logger
from ..core.validator import Validator


class GenericPredictor:
    def __init__(self, config_manager: ConfigManager, subject_name: str):
        self.config_manager = config_manager
        self.subject_name = subject_name
        self.model_dir = Path(self.config_manager.get('model_path')) / subject_name
        self.model_file = self.model_dir / self.config_manager.get('default_model_name')
        self.vectorizer = None
        self.model = None
        self.load_model()

    def load_model(self) -> bool:
        if not JOBLIB_AVAILABLE:
            logger.warning('joblib unavailable for %s predictor', self.subject_name)
            return False

        if not self.model_file.exists():
            logger.info('No model file for %s found at %s', self.subject_name, self.model_file)
            return False

        try:
            data = joblib.load(self.model_file)
            self.vectorizer = data.get('vectorizer')
            self.model = data.get('model')
            logger.info('Loaded predictor for %s', self.subject_name)
            return True
        except Exception as exc:
            logger.error('Failed to load predictor for %s: %s', self.subject_name, exc)
            self.vectorizer = None
            self.model = None
            return False

    def predict(self, email_data: Dict[str, Any]) -> str:
        if self.model is None or self.vectorizer is None:
            return 'unknown'

        text = ' '.join(filter(None, [Validator.normalize_text(email_data.get('title')), Validator.normalize_text(email_data.get('description'))]))
        if not text:
            return 'unknown'

        try:
            features = self.vectorizer.transform([text])
            prediction = self.model.predict(features)[0]
            return 'spam' if int(prediction) == 1 else 'ham'
        except Exception as exc:
            logger.error('Prediction failed for %s: %s', self.subject_name, exc)
            return 'unknown'

    def predict_proba(self, email_data: Dict[str, Any]) -> float:
        if self.model is None or self.vectorizer is None:
            return 0.0

        try:
            text = ' '.join(filter(None, [Validator.normalize_text(email_data.get('title')), Validator.normalize_text(email_data.get('description'))]))
            features = self.vectorizer.transform([text])
            if hasattr(self.model, 'predict_proba'):
                return float(self.model.predict_proba(features)[0][1])
            return 0.0
        except Exception as exc:
            logger.error('Probability failed for %s: %s', self.subject_name, exc)
            return 0.0
