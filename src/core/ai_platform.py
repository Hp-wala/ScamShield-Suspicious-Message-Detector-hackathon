from pathlib import Path
from typing import Any, Dict, List, Optional

from .config_manager import ConfigManager
from .dataset_manager import DatasetManager
from .intent_router import IntentRouter
from .knowledge_index import KnowledgeIndex
from .language_manager import LanguageManager
from .learning_system import LearningSystem
from .metadata_store import MetadataStore
from .model_manager import ModelManager
from .module_registry import ModuleRegistry
from .plugin_manager import PluginManager
from .search_engine import SearchEngine
from .subject_module import GenericSubjectModule
from .update_manager import UpdateManager
from .version_manager import VersionManager
from .knowledge_graph import KnowledgeGraph
from .logger import logger
from .conversation_engine import ConversationEngine
from .dataset_watcher import DatasetWatcher


class AIPlatform:
    def __init__(self, config: Optional[ConfigManager] = None) -> None:
        self.config_manager = config or ConfigManager()
        self.config_manager.ensure_paths()

        self.dataset_manager = DatasetManager(self.config_manager)
        self.module_registry = ModuleRegistry()
        self.plugin_manager = PluginManager()
        self.metadata_store = MetadataStore(Path(self.config_manager.get('cache_path')) / 'metadata')
        self.model_manager = ModelManager(self.config_manager)
        self.version_manager = VersionManager(Path(self.config_manager.get('cache_path')) / 'versions')
        self.knowledge_graph = KnowledgeGraph(Path(self.config_manager.get('cache_path')) / 'knowledge_graph.json')
        self.language_manager = LanguageManager()
        self.learning_system = LearningSystem(Path(self.config_manager.get('cache_path')) / 'learning_queue.json')
        self.knowledge_index = KnowledgeIndex(self.dataset_manager, self.metadata_store)
        self.search_engine = SearchEngine(self.dataset_manager, self.knowledge_index)
        self.intent_router = IntentRouter(self.dataset_manager, self.module_registry)
        self.update_manager = UpdateManager(self)
        self.conversation_engine = ConversationEngine(self)

        # start dataset watcher in background
        try:
            self.dataset_watcher = DatasetWatcher(self)
            self.dataset_watcher.start()
        except Exception as exc:
            logger.error('Failed to start DatasetWatcher: %s', exc)

        self.discover_modules()

    def discover_modules(self) -> None:
        self.module_registry.clear()
        self.plugin_manager.discover_plugins(Path(self.config_manager.get('root_path')) / 'plugins')

        for subject in self.dataset_manager.list_subjects():
            module = GenericSubjectModule(self.dataset_manager, subject)
            self.module_registry.register(module)
            try:
                module.initialize()
            except Exception as exc:
                logger.error('Failed to initialize module %s: %s', subject, exc)

    def refresh(self) -> None:
        logger.info('Refreshing AI platform datasets and modules')
        self.dataset_manager.refresh()
        self.discover_modules()

    def list_subjects(self) -> List[str]:
        return self.module_registry.list_plugins()

    def get_module(self, subject: str) -> Optional[GenericSubjectModule]:
        return self.module_registry.get(subject)

    def search(self, query: str, subjects: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        return self.search_engine.search(query, subjects)

    def answer(self, query: str) -> Dict[str, Any]:
        return self.conversation_engine.answer(query)

    def route(self, query: str) -> List[str]:
        return self.intent_router.route(query)
