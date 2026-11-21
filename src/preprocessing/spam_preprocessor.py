import re
from typing import Dict, Optional

from src.core.validator import Validator


class SpamPreprocessor:
    URL_PATTERN = re.compile(r'https?://\S+|www\.\S+', re.IGNORECASE)
    HEADER_PATTERN = re.compile(r'\b(From|To|Subject|Reply-To|Message-ID|Return-Path|Received):', re.IGNORECASE)

    @staticmethod
    def extract_text_fields(email_data: Dict[str, Optional[str]]) -> str:
        subject = Validator.normalize_text(email_data.get('subject'))
        body = Validator.normalize_text(email_data.get('body'))
        sender = Validator.normalize_text(email_data.get('from'))
        recipient = Validator.normalize_text(email_data.get('to'))
        reply_to = Validator.normalize_text(email_data.get('reply_to'))
        headers = Validator.normalize_text(email_data.get('headers'))

        return ' '.join(filter(None, [subject, body, sender, recipient, reply_to, headers]))

    @staticmethod
    def extract_urls(text: str) -> int:
        return len(SpamPreprocessor.URL_PATTERN.findall(text))

    @staticmethod
    def clean_text(text: str) -> str:
        text = Validator.normalize_text(text)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
