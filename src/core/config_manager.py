import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    root_path: Path
    database_path: Path
    debug: bool = False


class ConfigManager:
    def __init__(self) -> None:
        root = Path(__file__).resolve().parents[2]
        self.config = Config(
            root_path=root,
            database_path=root / "data" / "scamshield.db",
            debug=os.getenv("FLASK_DEBUG", "").lower() in {"1", "true", "yes"},
        )

    def get(self, key: str, default=None):
        return getattr(self.config, key, default)
