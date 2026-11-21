from pathlib import Path
from typing import Dict, Optional, Protocol


class ModulePlugin(Protocol):
    name: str

    def initialize(self) -> None:
        ...


class PluginManager:
    def __init__(self):
        self._plugins: Dict[str, ModulePlugin] = {}
        self._plugin_paths: Dict[str, Path] = {}

    def register(self, plugin: ModulePlugin) -> None:
        self._plugins[plugin.name] = plugin

    def get(self, name: str) -> Optional[ModulePlugin]:
        return self._plugins.get(name)

    def list_plugins(self) -> list[str]:
        return list(self._plugins.keys())

    def discover_plugins(self, plugin_dir: Path) -> None:
        if not plugin_dir.exists():
            return
        for path in sorted(plugin_dir.iterdir()):
            if path.is_dir():
                plugin_name = path.name
                self._plugin_paths[plugin_name] = path

    def list_available_plugins(self) -> list[str]:
        return sorted(self._plugin_paths.keys())

    def initialize_all(self) -> None:
        for plugin in self._plugins.values():
            try:
                plugin.initialize()
            except Exception:
                pass
