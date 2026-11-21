from typing import Any, Dict, List, Optional

from .intent_router import IntentRouter
from .search_engine import SearchEngine
from .logger import logger


class ConversationEngine:
    def __init__(self, platform: Any) -> None:
        self.platform = platform
        self.intent_router = IntentRouter(self.platform.dataset_manager, self.platform.module_registry)
        self.search_engine = SearchEngine(self.platform.dataset_manager, self.platform.knowledge_index)

    def answer(self, query: str, language: Optional[str] = None) -> Dict[str, Any]:
        route = self.intent_router.route(query)
        results = self.search_engine.search(query, route)
        graph_concepts = self.platform.knowledge_graph.expand_concepts([query])
        response = self.build_response(query, route, results, graph_concepts)
        return response

    def build_response(self, query: str, route: List[str], results: List[Dict[str, Any]], graph_concepts: List[str]) -> Dict[str, Any]:
        summary = f"Query routed to: {', '.join(route)}" if route else 'No route found.'
        if results:
            answer_text = ' '.join(
                [item.get('description', item.get('title', '')) for item in results[:3]]
            )
        else:
            answer_text = 'No answer available from current knowledge base.'

        sources = [item['dataset'] for item in results[:3] if 'dataset' in item]
        confidence = 0.0
        if results:
            confidence = min(1.0, 0.3 + len(results) * 0.15)

        return {
            'query': query,
            'route': route,
            'answer': answer_text,
            'sources': sources,
            'confidence': confidence,
            'summary': summary,
            'graph_concepts': graph_concepts,
            'metadata': {
                'results_found': len(results),
                'knowledge_graph_related': len(graph_concepts),
                'module': route[0] if route else None,
            },
        }
