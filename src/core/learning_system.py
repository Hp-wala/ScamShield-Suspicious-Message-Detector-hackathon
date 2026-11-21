from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

from .memory_store import MemoryStore
from .logger import logger


class LearningSystem:
    """Records unanswered queries and candidate knowledge for review.

    - Stores items in MemoryStore under 'learning_queue'.
    - Provides methods to list, approve, and reject learning items.
    """

    def __init__(self, memory_file: Path):
        self.memory = MemoryStore(memory_file)

    def record_unanswered(self, query: str, context: Dict[str, Any]) -> None:
        item = {'query': query, 'context': context, 'recorded_at': datetime.utcnow().isoformat(), 'status': 'pending'}
        try:
            self.memory.add_correction(item)
        except Exception:
            logger.exception('Failed to record unanswered query')

    def list_pending(self) -> List[Dict[str, Any]]:
        return [c for c in self.memory.list_corrections() if c.get('status') == 'pending']

    def approve(self, item_index: int) -> bool:
        # naive approach: update the correction entry status
        try:
            data = self.memory._read()
            corrections = data.get('corrections', [])
            if 0 <= item_index < len(corrections):
                corrections[item_index]['status'] = 'approved'
                corrections[item_index]['approved_at'] = datetime.utcnow().isoformat()
                self.memory._write(data)
                return True
        except Exception:
            logger.exception('Failed to approve learning item')
        return False

    def reject(self, item_index: int) -> bool:
        try:
            data = self.memory._read()
            corrections = data.get('corrections', [])
            if 0 <= item_index < len(corrections):
                corrections[item_index]['status'] = 'rejected'
                corrections[item_index]['rejected_at'] = datetime.utcnow().isoformat()
                self.memory._write(data)
                return True
        except Exception:
            logger.exception('Failed to reject learning item')
        return False
