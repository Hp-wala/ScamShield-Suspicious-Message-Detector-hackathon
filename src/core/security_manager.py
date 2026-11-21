from pathlib import Path
from typing import Any, Dict

from .config_manager import ConfigManager
from .logger import logger


class SecurityManager:
    def __init__(self, config: ConfigManager) -> None:
        self.config = config

    def validate_config(self) -> Dict[str, Any]:
        results = {
            'safe_dataset_path': self._is_safe_path(self.config.get('datasets_path')),
            'safe_model_path': self._is_safe_path(self.config.get('model_path')),
            'safe_cache_path': self._is_safe_path(self.config.get('cache_path')),
        }
        logger.info('Security validation results: %s', results)
        return results

    def _is_safe_path(self, path: Path) -> bool:
        try:
            path = Path(path)
            return path.exists() and path.is_absolute()
        except Exception:
            return False
