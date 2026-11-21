from typing import Any, Dict, List, Optional
from pathlib import Path

from .config_manager import ConfigManager
from .ai_platform import AIPlatform
from .learning_system import LearningSystem
from .memory_store import MemoryStore
from .logger import logger


class Brain:
    """Central coordinator and decision layer above AIPlatform.

    Brain understands user intent, routes the query, coordinates module
    selection, checks memory, consults the knowledge graph, and returns
    unified responses with metadata.
    """

    def __init__(self, config: Optional[ConfigManager] = None) -> None:
        self.config = config or ConfigManager()
        self.config.ensure_paths()

        self.platform = AIPlatform(self.config)
        self.memory = MemoryStore(Path(self.config.get('cache_path')) / 'memory_store.json')
        self.learning_system = self.platform.learning_system
        self.language_manager = self.platform.language_manager

    def answer(self, query: str, language: Optional[str] = None) -> Dict[str, Any]:
        try:
            plan = self.plan(query)
            response = self.execute(plan)
            localized = self.language_manager.translate_response(response, language)
            self._store_summary(query, localized)
            if localized.get('confidence', 0.0) < 0.3 or not localized.get('answer'):
                self.learning_system.record_unanswered(query, {'plan': plan, 'response': localized})
            return localized
        except Exception as exc:
            logger.error('Brain.answer failed: %s', exc)
            fallback = {
                'query': query,
                'route': [],
                'answer': 'I could not process that request.',
                'confidence': 0.0,
                'sources': [],
                'module': None,
                'metadata': {},
            }
            self._store_summary(query, fallback)
            return fallback

    def plan(self, query: str) -> Dict[str, Any]:
        route = self.platform.route(query)
        return {
            'query': query,
            'route': route,
            'module': route[0] if route else None,
            'subjects': route,
        }

    def execute(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        query = plan['query']
        route = plan['route']

        results = self.platform.search(query, route)
        graph_concepts = self.platform.knowledge_graph.expand_concepts([query])

        response = self.platform.conversation_engine.build_response(query, route, results, graph_concepts)
        response['module'] = plan['module']
        response['subjects'] = route
        response['graph_concepts'] = graph_concepts
        response['learning_pending'] = len(self.learning_system.list_pending())
        return response

    def summarize_context(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.memory.list_summaries(limit)

    def get_memory(self) -> MemoryStore:
        return self.memory

    def get_pending_learning(self) -> List[Dict[str, Any]]:
        return self.learning_system.list_pending()

    def _store_summary(self, query: str, result: Dict[str, Any]) -> None:
        try:
            self.memory.add_conversation_summary({
                'query': query,
                'answer': result.get('answer', ''),
                'route': result.get('route', []),
                'module': result.get('module'),
                'confidence': float(result.get('confidence', 0.0)),
            })
        except Exception:
            logger.exception('Failed to persist conversation summary')
