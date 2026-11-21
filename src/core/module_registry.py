from pathlib import Path
from typing import Dict, Optional

from .logger import logger


class ModuleRegistry:
    def __init__(self):
        self._modules: Dict[str, object] = {}

    def register(self, module: object) -> None:
        name = getattr(module, 'name', None)
        if name:
            self._modules[name] = module
            logger.info('Registered module: %s', name)

    def get(self, name: str) -> Optional[object]:
        return self._modules.get(name)

    def list_plugins(self) -> list[str]:
        return sorted(self._modules.keys())

    def list_subjects(self) -> list[str]:
        return self.list_plugins()

    def clear(self) -> None:
        self._modules.clear()
