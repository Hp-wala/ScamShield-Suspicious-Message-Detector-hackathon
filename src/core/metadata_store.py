import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .logger import logger


class MetadataStore:
    def __init__(self, metadata_dir: Path) -> None:
        self.metadata_dir = metadata_dir
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

    def save_metadata(self, dataset_name: str, metadata: Dict[str, Any]) -> bool:
        try:
            metadata_file = self._metadata_file(dataset_name)
            metadata_file.parent.mkdir(parents=True, exist_ok=True)
            metadata['last_updated'] = datetime.utcnow().isoformat()
            with metadata_file.open('w', encoding='utf-8') as handle:
                json.dump(metadata, handle, ensure_ascii=False, indent=2)
            return True
        except Exception as exc:
            logger.error('Failed to save metadata for %s: %s', dataset_name, exc)
            return False

    def load_metadata(self, dataset_name: str) -> Dict[str, Any]:
        metadata_file = self._metadata_file(dataset_name)
        if not metadata_file.exists():
            return {}

        try:
            with metadata_file.open('r', encoding='utf-8') as handle:
                return json.load(handle)
        except Exception as exc:
            logger.error('Failed to load metadata for %s: %s', dataset_name, exc)
            return {}

    def _metadata_file(self, dataset_name: str) -> Path:
        return self.metadata_dir / f'{dataset_name}.meta.json'
