import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .config_manager import ConfigManager
from .logger import logger


class DatasetWatcher:
    def __init__(self, platform: Any, poll_interval: float = 2.0) -> None:
        self.platform = platform
        self.config: ConfigManager = platform.config_manager
        self.datasets_path: Path = Path(self.config.get('datasets_path'))
        self.poll_interval = float(poll_interval)
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._snapshot: Dict[str, Tuple[float, int]] = {}
        self._last_processed: Dict[str, Tuple[float, int]] = {}
        self._lock = threading.RLock()

        # build initial snapshot
        try:
            self._snapshot = self._scan_snapshot()
        except Exception:
            self._snapshot = {}

    def _scan_snapshot(self) -> Dict[str, Tuple[float, int]]:
        snapshot: Dict[str, Tuple[float, int]] = {}
        for path in sorted(self.datasets_path.rglob('*')):
            if not path.is_file():
                continue
            try:
                st = path.stat()
                snapshot[str(path)] = (st.st_mtime, st.st_size)
            except Exception:
                continue
        return snapshot

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name='DatasetWatcher')
        self._thread.start()
        logger.info('DatasetWatcher started (poll=%ss)', self.poll_interval)

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        logger.info('DatasetWatcher stopped')

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                self.scan_once()
            except Exception as exc:
                logger.error('DatasetWatcher scan failed: %s', exc)
            time.sleep(self.poll_interval)

    def scan_once(self) -> None:
        """Run a single scan cycle (callable from tests)."""
        with self._lock:
            current = self._scan_snapshot()
            added = [Path(p) for p in current.keys() if p not in self._snapshot]
            removed = [Path(p) for p in self._snapshot.keys() if p not in current]
            modified = []

            for p, (mtime, size) in current.items():
                old = self._snapshot.get(p)
                if old and (old[0] != mtime or old[1] != size):
                    modified.append(Path(p))

            if not added and not removed and not modified:
                return

            # update snapshot immediately to avoid reprocessing same events
            self._snapshot = current

        # process removals first
        for path in removed:
            try:
                self._handle_removed(path)
            except Exception as exc:
                logger.error('Error handling removed dataset %s: %s', path, exc)

        # process additions and modifications
        for path in added + modified:
            try:
                self._handle_change(path)
            except Exception as exc:
                logger.error('Error handling dataset change %s: %s', path, exc)

    def _handle_removed(self, path: Path) -> None:
        dataset_manager = self.platform.dataset_manager
        dataset_key = dataset_manager._dataset_key(path) if path.exists() else self._path_to_key(path)
        logger.info('Dataset removed: %s', dataset_key)
        # refresh registry and mark metadata
        try:
            dataset_manager.refresh()
            metadata = self.platform.metadata_store.load_metadata(dataset_key)
            metadata['deleted'] = True
            metadata['index_status'] = 'removed'
            self.platform.metadata_store.save_metadata(dataset_key, metadata)
            self.platform.update_manager.schedule_refresh()
        except Exception as exc:
            logger.error('Failed to process removal for %s: %s', dataset_key, exc)

    def _handle_change(self, path: Path) -> None:
        dataset_manager = self.platform.dataset_manager
        # ensure dataset registry is aware and cache is cleared
        dataset_manager.refresh()
        try:
            dataset_key = dataset_manager._dataset_key(path)
        except Exception:
            dataset_key = self._path_to_key(path)

        # avoid duplicate processing: check last processed
        try:
            st = path.stat()
            current_sig = (st.st_mtime, st.st_size)
        except Exception:
            current_sig = (0.0, 0)

        last = self._last_processed.get(str(path))
        if last == current_sig:
            logger.debug('Skipping duplicate event for %s', path)
            return

        logger.info('Dataset changed: %s', dataset_key)

        # attempt to (re)load and reindex the dataset
        rows = []
        try:
            rows = dataset_manager.load_dataset(dataset_key)
            metadata = self.platform.metadata_store.load_metadata(dataset_key) or {}
            # versioning: bump version
            version = int(metadata.get('version', 0)) + 1
            metadata.update({
                'dataset': dataset_key,
                'last_modified': time.ctime(current_sig[0]),
                'import_date': time.ctime(),
                'version': version,
                'record_count': len(rows) if rows else 0,
                'validation_status': 'ok' if rows else 'empty',
                'index_status': 'indexed' if rows else 'empty',
            })
            self.platform.metadata_store.save_metadata(dataset_key, metadata)
            # trigger a higher-level refresh for modules/plugins
            self.platform.update_manager.schedule_refresh()
        finally:
            self._last_processed[str(path)] = current_sig

    def _path_to_key(self, path: Path) -> str:
        try:
            rel = path.relative_to(self.datasets_path).with_suffix('')
            return rel.as_posix()
        except Exception:
            return path.name

    def trigger_refresh(self) -> None:
        """Manual trigger to perform a scan and processing."""
        self.scan_once()
