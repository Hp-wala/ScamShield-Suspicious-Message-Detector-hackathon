import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .logger import logger


class VersionManager:
    def __init__(self, version_dir: Path) -> None:
        self.version_dir = Path(version_dir)
        self.version_dir.mkdir(parents=True, exist_ok=True)

    def _version_file(self, dataset_name: str, version: int) -> Path:
        safe_name = dataset_name.replace('/', '_').replace('\\', '_')
        return self.version_dir / f'{safe_name}_v{version}.json'

    def _latest_metadata_path(self, dataset_name: str) -> Path:
        safe_name = dataset_name.replace('/', '_').replace('\\', '_')
        return self.version_dir / f'{safe_name}_latest.json'

    def record_version(self, dataset_name: str, source_path: Path, record_count: int, validation_status: str, changes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        metadata = self.load_latest(dataset_name) or {}
        version = int(metadata.get('version', 0)) + 1
        payload = {
            'dataset': dataset_name,
            'version': version,
            'timestamp': datetime.utcnow().isoformat(),
            'source_path': str(source_path),
            'record_count': record_count,
            'validation_status': validation_status,
            'changes': changes or {},
            'hash': self._hash_path(source_path),
        }
        version_file = self._version_file(dataset_name, version)
        try:
            with version_file.open('w', encoding='utf-8') as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
            with self._latest_metadata_path(dataset_name).open('w', encoding='utf-8') as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
            logger.info('Recorded dataset version %s for %s', version, dataset_name)
            return payload
        except Exception as exc:
            logger.error('Failed to record dataset version for %s: %s', dataset_name, exc)
            return payload

    def _hash_path(self, source_path: Path) -> str:
        try:
            hasher = hashlib.sha256()
            with source_path.open('rb') as handle:
                while True:
                    chunk = handle.read(8192)
                    if not chunk:
                        break
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ''

    def load_latest(self, dataset_name: str) -> Optional[Dict[str, Any]]:
        path = self._latest_metadata_path(dataset_name)
        if not path.exists():
            return None
        try:
            with path.open('r', encoding='utf-8') as handle:
                return json.load(handle)
        except Exception as exc:
            logger.error('Failed to load latest version metadata for %s: %s', dataset_name, exc)
            return None

    def list_versions(self, dataset_name: str) -> List[Dict[str, Any]]:
        safe_name = dataset_name.replace('/', '_').replace('\\', '_')
        versions = []
        for path in sorted(self.version_dir.glob(f'{safe_name}_v*.json')):
            try:
                with path.open('r', encoding='utf-8') as handle:
                    versions.append(json.load(handle))
            except Exception:
                continue
        return versions

    def restore_version(self, dataset_name: str, version: int) -> Optional[Dict[str, Any]]:
        path = self._version_file(dataset_name, version)
        if not path.exists():
            return None
        try:
            with path.open('r', encoding='utf-8') as handle:
                return json.load(handle)
        except Exception as exc:
            logger.error('Failed to restore version %s for %s: %s', version, dataset_name, exc)
            return None
