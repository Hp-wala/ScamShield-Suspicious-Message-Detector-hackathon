import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.core.knowledge_pipeline.base_extractor import BaseExtractor
from src.core.knowledge_pipeline.extractor_registry import registry
from src.core.knowledge_pipeline.stages.metadata_stage import MetadataStage
from src.core.schema_mapper import SchemaMapper
from src.core.validator import Validator


class SqliteExtractor(BaseExtractor):
    def validate(self, path: Path) -> bool:
        return path.suffix.lower() in ('.sqlite', '.db') and path.exists()

    def _first_table(self, conn: sqlite3.Connection) -> Optional[str]:
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name LIMIT 1"
        )
        row = cur.fetchone()
        return row[0] if row else None

    def extract(self, path: Path) -> Tuple[Optional[List[Dict[str, Any]]], Dict[str, Any]]:
        try:
            conn = sqlite3.connect(str(path))
            table = self._first_table(conn)
            if not table:
                return None, {'status': 'empty'}

            cur = conn.execute(f'SELECT * FROM "{table}"')
            cols = [d[0] for d in cur.description]
            schema_mapper = SchemaMapper()
            header_map = schema_mapper.map_headers(cols)
            if header_map is None:
                header_map = {c: 'metadata' for c in cols}

            rows: List[Dict[str, Any]] = []
            for row in cur.fetchall():
                cleaned = {cols[i]: Validator.normalize_text(row[i]) for i in range(len(cols))}
                rows.append(schema_mapper.map_row(cleaned, header_map))

            conn.close()
            return rows, {'status': 'ok'}
        except Exception as exc:
            return None, {'status': 'error', 'reason': str(exc)}

    def metadata(self, path: Path) -> Dict[str, Any]:
        return MetadataStage().create(str(path), path.name, 'sqlite', path.stem, 0.8, 0, [], 'pending')


registry.register('sqlite', SqliteExtractor())
registry.register('db', SqliteExtractor())
