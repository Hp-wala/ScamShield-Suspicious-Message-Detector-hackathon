from pathlib import Path
from typing import Any, Dict, List

from src.core.validator import Validator


class TopicStage:
    def detect(self, rows: List[Dict[str, Any]], file_name: str, subject: str) -> Dict[str, Any]:
        topic_candidates: List[str] = []
        confidence = 0.0

        if subject:
            topic_candidates.append(subject)
            confidence = max(confidence, 0.8)

        if Path(file_name).stem:
            topic_candidates.append(Path(file_name).stem)
            confidence = max(confidence, 0.7)

        for row in rows:
            for field in ('subject', 'topic', 'category', 'title'):
                value = Validator.normalize_text(row.get(field, ''))
                if value:
                    topic_candidates.append(value)
                    confidence = max(confidence, 0.65)

        content_text = ' '.join(str(v) for row in rows for v in row.values())
        if content_text:
            words = [token.strip('.,()[]{}"\'':;!?').lower() for token in content_text.split() if len(token) > 3]
            if words:
                most_common = max(set(words), key=words.count)
                if Validator.is_valid_string(most_common):
                    topic_candidates.append(most_common)
                    confidence = max(confidence, 0.55)

        topic = next((candidate for candidate in topic_candidates if candidate), subject or Path(file_name).stem)
        return {'topic': topic, 'confidence': confidence}
