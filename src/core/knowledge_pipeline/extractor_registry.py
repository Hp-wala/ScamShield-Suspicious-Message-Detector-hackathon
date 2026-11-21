from pathlib import Path
from typing import Any, Dict, Optional

from .base_extractor import BaseExtractor


class ExtractorRegistry:
    def __init__(self) -> None:
        self._extractors: dict[str, BaseExtractor] = {}

    def register(self, ext: str, extractor: BaseExtractor) -> None:
        self._extractors[ext.lower().lstrip('.')] = extractor

    def get(self, path: Path) -> Optional[BaseExtractor]:
        return self._extractors.get(path.suffix.lower().lstrip('.'))

    def list_extractors(self) -> list[str]:
        return sorted(self._extractors.keys())


registry = ExtractorRegistry()
