import sqlite3
from datetime import datetime, timedelta, timezone
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
                    created_at TEXT NOT NULL
                )
                """
            )
            columns = {row[1] for row in connection.execute("PRAGMA table_info(reports)").fetchall()}
            if "created_at" not in columns:
                connection.execute("ALTER TABLE reports ADD COLUMN created_at TEXT")
                connection.execute("UPDATE reports SET created_at = COALESCE(timestamp, ?) WHERE created_at IS NULL",
                                   (datetime.now(timezone.utc).isoformat(),))
            if "timestamp" in columns:
                connection.execute("DROP TABLE IF EXISTS reports_legacy")

    def add(self, result: Dict[str, Any]) -> int:
        with self._connect() as connection:
            existing = connection.execute(
                "SELECT id FROM reports WHERE text_hash = ? LIMIT 1",
                (result["text_hash"],),
            ).fetchone()
            if existing:
                return -int(existing[0])
            now = datetime.now(timezone.utc).isoformat()
            columns = {row[1] for row in connection.execute("PRAGMA table_info(reports)").fetchall()}
            if "timestamp" in columns:
                cursor = connection.execute(
                    """
                    INSERT INTO reports (channel, category, risk_score, text_hash, created_at, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (result["channel"], result["category"], int(result["risk_score"]),
                     result["text_hash"], now, now),
                )
            else:
                cursor = connection.execute(
                    """
                    INSERT INTO reports (channel, category, risk_score, text_hash, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (result["channel"], result["category"], int(result["risk_score"]),
                     result["text_hash"], now),
                )
            return int(cursor.lastrowid)

    def recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT channel, category, risk_score, text_hash, created_at
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
            last_days = connection.execute(
                """
                SELECT substr(created_at, 1, 10) AS day, COUNT(*) AS count
                FROM reports
                WHERE created_at >= ?
                GROUP BY substr(created_at, 1, 10)
                ORDER BY day
                """,
                ((datetime.now(timezone.utc).date() - timedelta(days=6)).isoformat(),),
            ).fetchall()
            counts = {row["day"]: row["count"] for row in last_days}
            zero_filled = []
            for offset in range(6, -1, -1):
                day = (datetime.now(timezone.utc).date() - timedelta(days=offset)).isoformat()
                zero_filled.append({"day": day, "count": counts.get(day, 0)})
            return {
                "total_reports": total,
                "average_risk_score": round(float(average), 1),
                "categories": [dict(row) for row in categories],
                "channels": [dict(row) for row in channels],
                "by_category": {row["category"]: row["count"] for row in categories},
                "by_channel": {row["channel"]: row["count"] for row in channels},
                "last_7_days": zero_filled,
            }
