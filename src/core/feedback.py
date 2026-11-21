import sqlite3
from pathlib import Path


class FeedbackStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS feedback (channel TEXT, verdict TEXT, correct INTEGER)"
            )

    def add(self, channel: str, verdict: str, correct: bool) -> None:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                "INSERT INTO feedback (channel, verdict, correct) VALUES (?, ?, ?)",
                (channel, verdict, int(correct)),
            )
