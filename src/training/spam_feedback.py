import csv
from pathlib import Path
from typing import Dict

from src.core.logger import logger
from src.core.validator import Validator


class SpamFeedback:
    def __init__(self, feedback_path: Path):
        self.feedback_path = feedback_path
        self.feedback_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.feedback_path.exists():
            self.feedback_path.write_text(
                'subject,body,from,to,reply_to,headers,label,timestamp\n',
                encoding='utf-8',
            )

    def store_feedback(self, email_data: Dict[str, str], label: str, timestamp: str) -> bool:
        try:
            if label.strip().lower() not in {'spam', 'ham'}:
                logger.warning('Feedback label invalid: %s', label)
                return False

            with self.feedback_path.open('a', encoding='utf-8', newline='') as handle:
                writer = csv.writer(handle)
                writer.writerow([
                    email_data.get('subject', ''),
                    email_data.get('body', ''),
                    email_data.get('from', ''),
                    email_data.get('to', ''),
                    email_data.get('reply_to', ''),
                    email_data.get('headers', ''),
                    label,
                    timestamp,
                ])
            logger.info('Stored feedback label=%s', label)
            return True
        except Exception as exc:
            logger.error('Failed to store feedback: %s', exc)
            return False
