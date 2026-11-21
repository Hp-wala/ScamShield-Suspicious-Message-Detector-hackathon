from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Config:
    root_path: Path
    datasets_path: Path
    model_path: Path
    logs_path: Path
    cache_path: Path
    feedback_file: Path
    cache_enabled: bool = True
    default_model_name: str = 'spam_detector.joblib'
    supported_dataset_extensions: tuple[str, ...] = (
        '.csv', '.json', '.txt', '.md', '.xml', '.xlsx', '.xls', '.sqlite', '.db', '.pdf', '.docx'
    )


ROOT_PATH = Path(__file__).resolve().parents[2]
DATASETS_PATH = ROOT_PATH / 'datasets'
MODEL_PATH = ROOT_PATH / 'models'
LOGS_PATH = ROOT_PATH / 'logs'
CACHE_PATH = ROOT_PATH / 'cache'
FEEDBACK_FILE = ROOT_PATH / 'datasets' / 'spam_detection' / 'user_feedback.csv'

DEFAULT_CONFIG = Config(
    root_path=ROOT_PATH,
    datasets_path=DATASETS_PATH,
    model_path=MODEL_PATH,
    logs_path=LOGS_PATH,
    cache_path=CACHE_PATH,
    feedback_file=FEEDBACK_FILE,
)


class ConfigManager:
    def __init__(self, config: Config = DEFAULT_CONFIG):
        self.config = config

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self.config, key, default)

    def ensure_paths(self) -> None:
        self.config.datasets_path.mkdir(parents=True, exist_ok=True)
        self.config.model_path.mkdir(parents=True, exist_ok=True)
        self.config.logs_path.mkdir(parents=True, exist_ok=True)
        self.config.cache_path.mkdir(parents=True, exist_ok=True)
        self.config.feedback_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.config.feedback_file.exists():
            self.config.feedback_file.write_text(
                'subject,body,from,to,reply_to,headers,label,timestamp\n',
                encoding='utf-8',
            )
