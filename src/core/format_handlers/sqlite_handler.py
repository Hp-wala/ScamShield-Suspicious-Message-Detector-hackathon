import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..schema_mapper import SchemaMapper
from ..validator import Validator
from ..logger import logger


class SqliteHandler:
    def __init__(self):
        self.schema_mapper = SchemaMapper()

    def _first_table(self, conn: sqlite3.Connection) -> Optional[str]:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name LIMIT 1")
        row = cur.fetchone()
        return row[0] if row else None

    def load(self, path: Path) -> Tuple[Optional[List[Dict[str, Any]]], Optional[Dict[str, str]], str]:
        try:
            conn = sqlite3.connect(str(path))
            table = self._first_table(conn)
            if not table:
                return None, None, 'empty'

            cur = conn.execute(f'SELECT * FROM "{table}"')
            cols = [d[0] for d in cur.description]
            rows = []
            header_map = self.schema_mapper.map_headers(cols)
            if header_map is None:
                # map headers from columns directly
                header_map = {c: 'metadata' for c in cols}

            for r in cur.fetchall():
                raw = {cols[i]: Validator.normalize_text(r[i]) for i in range(len(cols))}
                rows.append(self.schema_mapper.map_row(raw, header_map))

            conn.close()
            return rows, header_map, 'sqlite'
        except Exception as exc:
            logger.error('SqliteHandler failed to load %s: %s', path, exc)
            return None, None, 'error'
