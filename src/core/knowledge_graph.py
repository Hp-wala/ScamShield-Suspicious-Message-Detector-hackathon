from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class KnowledgeGraph:
    """Lightweight knowledge graph with JSON persistence support."""

    def __init__(self, storage_path: Optional[Path] = None) -> None:
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []
        self.storage_path = Path(storage_path) if storage_path else None
        if self.storage_path:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            self.load()

    def add_node(self, name: str, meta: Optional[Dict[str, Any]] = None) -> None:
        if name not in self.nodes:
            self.nodes[name] = {'name': name, 'meta': meta or {}}
        elif meta:
            self.nodes[name]['meta'].update(meta)

    def add_edge(self, source: str, target: str, relation: str) -> None:
        self.add_node(source)
        self.add_node(target)
        edge = {'source': source, 'target': target, 'relation': relation}
        if edge not in self.edges:
            self.edges.append(edge)

    def find_related(self, concept: str) -> List[Dict[str, Any]]:
        return [e for e in self.edges if e['source'] == concept or e['target'] == concept]

    def expand_concepts(self, seed_concepts: List[str], depth: int = 2) -> List[str]:
        seen = set(seed_concepts)
        frontier = list(seed_concepts)
        for _ in range(depth):
            next_frontier: List[str] = []
            for concept in frontier:
                for edge in self.find_related(concept):
                    partner = edge['target'] if edge['source'] == concept else edge['source']
                    if partner not in seen:
                        next_frontier.append(partner)
                        seen.add(partner)
            frontier = next_frontier
        return list(seen)

    def save(self) -> bool:
        if not self.storage_path:
            return False
        try:
            with self.storage_path.open('w', encoding='utf-8') as handle:
                json.dump({'nodes': self.nodes, 'edges': self.edges}, handle, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def load(self) -> bool:
        if not self.storage_path or not self.storage_path.exists():
            return False
        try:
            with self.storage_path.open('r', encoding='utf-8') as handle:
                payload = json.load(handle)
                self.nodes = payload.get('nodes', {})
                self.edges = payload.get('edges', [])
            return True
        except Exception:
            return False

    def get_entity(self, name: str) -> Optional[Dict[str, Any]]:
        return self.nodes.get(name)

    def list_entities(self) -> List[str]:
        return sorted(self.nodes.keys())
