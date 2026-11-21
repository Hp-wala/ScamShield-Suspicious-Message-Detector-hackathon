from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


class BaseExtractor(ABC):
    @abstractmethod
    def validate(self, path: Path) -> bool:
        raise NotImplementedError

    @abstractmethod
    def extract(self, path: Path) -> Tuple[Optional[list[dict[str, Any]]], Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def metadata(self, path: Path) -> Dict[str, Any]:
        raise NotImplementedError
