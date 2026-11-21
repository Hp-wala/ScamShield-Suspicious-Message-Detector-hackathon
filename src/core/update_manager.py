from pathlib import Path
from typing import Any

from .logger import logger


class UpdateManager:
    def __init__(self, platform: Any) -> None:
        self.platform = platform

    def scan_for_updates(self) -> None:
        self.platform.dataset_manager.refresh()
        self.platform.discover_modules()
        logger.info('Update scan complete')

    def schedule_refresh(self) -> None:
        try:
            self.scan_for_updates()
        except Exception as exc:
            logger.error('Update refresh failed: %s', exc)
