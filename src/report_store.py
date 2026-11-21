import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


class ReportStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel TEXT NOT NULL,
                    category TEXT NOT NULL,
                    risk_score INTEGER NOT NULL,
                    text_hash TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
                """
            )

    def add(self, result: Dict[str, Any]) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO reports (channel, category, risk_score, text_hash, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    result["channel"],
                    result["category"],
                    int(result["risk_score"]),
                    result["text_hash"],
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            return int(cursor.lastrowid)

    def recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT channel, category, risk_score, text_hash, timestamp
                FROM reports ORDER BY id DESC LIMIT ?
                """,
                (max(1, min(limit, 100)),),
            ).fetchall()
            return [dict(row) for row in rows]

    def stats(self) -> Dict[str, Any]:
        with self._connect() as connection:
            total = connection.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
            categories = connection.execute(
                "SELECT category, COUNT(*) AS count FROM reports GROUP BY category ORDER BY count DESC"
            ).fetchall()
            channels = connection.execute(
                "SELECT channel, COUNT(*) AS count FROM reports GROUP BY channel ORDER BY count DESC"
            ).fetchall()
            average = connection.execute(
                "SELECT COALESCE(AVG(risk_score), 0) FROM reports"
            ).fetchone()[0]
            return {
                "total_reports": total,
                "average_risk_score": round(float(average), 1),
                "categories": [dict(row) for row in categories],
                "channels": [dict(row) for row in channels],
            }
