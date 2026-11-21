from typing import Any, Dict, List

from .config_manager import ConfigManager
from .dataset_manager import DatasetManager
from .logger import logger


class DiagnosticsManager:
    def __init__(self, config_manager: ConfigManager, dataset_manager: DatasetManager) -> None:
        self.config_manager = config_manager
        self.dataset_manager = dataset_manager

    def run_checks(self) -> Dict[str, Any]:
        report: Dict[str, Any] = {
            'datasets': self._check_datasets(),
            'config': self._check_config(),
            'cache': self._check_cache(),
        }
        logger.info('Diagnostics completed: %s', report)
        return report

    def _check_datasets(self) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        for dataset_name, entry in self.dataset_manager.registry.items():
            status = entry.get('status', 'unknown')
            if status not in {'csv', 'json'}:
                findings.append({'dataset': dataset_name, 'issue': f'invalid status {status}'})
        return findings

    def _check_config(self) -> Dict[str, Any]:
        return {'root_path_exists': self.config_manager.get('root_path').exists()}

    def _check_cache(self) -> Dict[str, Any]:
        return {'cache_path_exists': self.config_manager.get('cache_path').exists()}
