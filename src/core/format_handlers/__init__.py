from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .csv_handler import CsvHandler
from .json_handler import JsonHandler
from .txt_handler import TxtHandler
from .md_handler import MdHandler
from .html_handler import HtmlHandler
from .sqlite_handler import SqliteHandler


class FormatHandlerRegistry:
    def __init__(self):
        self._handlers = {}
        # register built-in handlers
        self.register('csv', CsvHandler())
        self.register('json', JsonHandler())
        self.register('txt', TxtHandler())
        self.register('md', MdHandler())
        self.register('html', HtmlHandler())
        self.register('sqlite', SqliteHandler())

    def register(self, ext: str, handler: Any) -> None:
        self._handlers[ext.lower().lstrip('.')] = handler

    def get(self, ext: str) -> Optional[Any]:
        return self._handlers.get(ext.lower().lstrip('.'))

    def load(self, path: Path) -> Tuple[Optional[list], Optional[dict], str]:
        ext = path.suffix.lower().lstrip('.')
        handler = self.get(ext)
        if handler:
            return handler.load(path)
        return None, None, 'unsupported'


registry = FormatHandlerRegistry()
