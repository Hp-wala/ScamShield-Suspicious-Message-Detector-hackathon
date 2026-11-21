from datetime import datetime
from src.core.config_manager import ConfigManager
from src.inference.spam_service import SpamService
from src.training.spam_feedback import SpamFeedback


class SpamModule:
    name = 'spam_detector'

    def __init__(self):
        self.config = ConfigManager()
        self.config.ensure_paths()
        self.service = SpamService(self.config)
        self.feedback = SpamFeedback(self.config.get('feedback_file'))

    def initialize(self) -> None:
        self.service.load_model()

    def predict(self, email_data):
        return self.service.predict(email_data)

    def predict_proba(self, email_data):
        return self.service.predict_proba(email_data)

    def retrain(self, dataset_name: str, model_type: str = 'logistic'):
        return self.service.retrain(dataset_name, model_type=model_type)

    def submit_feedback(self, email_data, label: str):
        timestamp = datetime.utcnow().isoformat()
        return self.feedback.store_feedback(email_data, label, timestamp)
