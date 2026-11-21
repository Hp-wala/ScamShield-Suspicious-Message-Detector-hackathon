import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from .logger import logger


class MemoryStore:
    """Simple JSON-backed memory store.

    Designed to be lightweight and replaceable; stores data in one file
    and exposes APIs for preferences, conversation summaries, approved
    schema mappings, corrections, and user feedback.
    """

    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._write({'preferences': {}, 'summaries': [], 'schema_approvals': [], 'corrections': [], 'feedback': []})

    def _read(self) -> Dict[str, Any]:
        try:
            with self.file_path.open('r', encoding='utf-8') as handle:
                return json.load(handle)
        except Exception:
            logger.exception('Failed to read memory store; resetting file')
            self._write({'preferences': {}, 'summaries': [], 'schema_approvals': [], 'corrections': [], 'feedback': []})
            return self._read()

    def _write(self, data: Dict[str, Any]) -> None:
        try:
            with self.file_path.open('w', encoding='utf-8') as handle:
                json.dump(data, handle, ensure_ascii=False, indent=2)
        except Exception:
            logger.exception('Failed to write memory store')

    # Preferences
    def set_preference(self, key: str, value: Any) -> None:
        data = self._read()
        data.setdefault('preferences', {})[key] = value
        self._write(data)

    def get_preference(self, key: str, default: Any = None) -> Any:
        data = self._read()
        return data.get('preferences', {}).get(key, default)

    # Conversation summaries
    def add_conversation_summary(self, summary: Dict[str, Any]) -> None:
        data = self._read()
        summary_record = dict(summary)
        summary_record.setdefault('created_at', datetime.utcnow().isoformat())
        data.setdefault('summaries', []).insert(0, summary_record)
        # keep a bounded history of 500 summaries
        data['summaries'] = data['summaries'][:500]
        self._write(data)

    def list_summaries(self, limit: int = 20) -> List[Dict[str, Any]]:
        data = self._read()
        return data.get('summaries', [])[:limit]

    # Schema approvals
    def approve_schema_mapping(self, dataset_name: str, mapping: Dict[str, str]) -> None:
        data = self._read()
        data.setdefault('schema_approvals', []).append({'dataset': dataset_name, 'mapping': mapping, 'approved_at': datetime.utcnow().isoformat()})
        self._write(data)

    def list_schema_approvals(self) -> List[Dict[str, Any]]:
        data = self._read()
        return data.get('schema_approvals', [])

    # Corrections
    def add_correction(self, item: Dict[str, Any]) -> None:
        data = self._read()
        item_record = dict(item)
        item_record.setdefault('created_at', datetime.utcnow().isoformat())
        data.setdefault('corrections', []).append(item_record)
        self._write(data)

    def list_corrections(self) -> List[Dict[str, Any]]:
        data = self._read()
        return data.get('corrections', [])

    # Feedback
    def add_feedback(self, feedback: Dict[str, Any]) -> None:
        data = self._read()
        fb = dict(feedback)
        fb.setdefault('created_at', datetime.utcnow().isoformat())
        data.setdefault('feedback', []).append(fb)
        self._write(data)

    def list_feedback(self) -> List[Dict[str, Any]]:
        data = self._read()
        return data.get('feedback', [])
