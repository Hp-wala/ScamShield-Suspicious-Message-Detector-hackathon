from typing import Any, Dict, List

from src.core.knowledge_graph import KnowledgeGraph
from src.core.validator import Validator


class EntityStage:
    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph

    def extract(self, rows: List[Dict[str, Any]], dataset_key: str) -> List[Dict[str, Any]]:
        entities: List[Dict[str, Any]] = []

        for row in rows:
            text = ' '.join(str(value) for value in row.values() if Validator.is_valid_string(value))
            tokens = {token.strip('.,()[]{}"\'':;!?').title() for token in text.split() if token.istitle() and len(token) > 1}
            for token in sorted(tokens):
                entity = {'entity': token, 'type': 'unknown', 'source': row.get('title', dataset_key)}
                entities.append(entity)
                self.graph.add_node(token, {'source': dataset_key})
                self.graph.add_edge(dataset_key, token, 'mentions')

        self.graph.save()
        return entities
