from pathlib import Path
from typing import Any, Dict, List, Optional

from .config_manager import ConfigManager
from .logger import logger

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    joblib = None
    JOBLIB_AVAILABLE = False
    logger.warning('joblib is unavailable. Model saving and loading are disabled.')


class ModelManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.model_dir = Path(self.config_manager.get('model_path'))
        self.model_dir.mkdir(parents=True, exist_ok=True)

    def get_model_path(self, model_name: str) -> Path:
        return self.model_dir / model_name

    def exists(self, model_name: str) -> bool:
        return self.get_model_path(model_name).exists()

    def save(self, model_name: str, data: Any) -> bool:
        if not JOBLIB_AVAILABLE:
            logger.warning('Cannot save model because joblib is unavailable.')
            return False

        try:
            target_path = self.get_model_path(model_name)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(data, target_path)
            logger.info('Saved model %s', target_path)
            # also persist metadata if available in the provided data
            try:
                metadata = None
                if isinstance(data, dict) and 'metadata' in data:
                    metadata = data.get('metadata')
                else:
                    # minimal metadata stub
                    metadata = {'model_name': model_name}
                self.save_metadata(model_name, metadata)
            except Exception:
                logger.exception('Failed to write model metadata for %s', model_name)
            return True
        except Exception as exc:
            logger.error('Failed to save model %s: %s', model_name, exc)
            return False

    def load(self, model_name: str) -> Optional[Any]:
        if not JOBLIB_AVAILABLE:
            logger.warning('Cannot load model because joblib is unavailable.')
            return None

        path = self.get_model_path(model_name)
        if not path.exists():
            logger.warning('Model not found: %s', path)
            return None

        try:
            obj = joblib.load(path)
            # Do not modify returned object to keep backward compatibility.
            return obj
        except Exception as exc:
            logger.error('Failed to load model %s: %s', model_name, exc)
            return None

    def metadata_path(self, model_name: str) -> Path:
        return self.get_model_path(f"{model_name}.meta.json")

    def list_models(self) -> List[str]:
        return sorted([path.name for path in self.model_dir.glob('*.joblib')])

    def save_metadata(self, model_name: str, metadata: Any) -> bool:
        try:
            meta_file = self.metadata_path(model_name)
            meta_file.parent.mkdir(parents=True, exist_ok=True)
            import json

            with meta_file.open('w', encoding='utf-8') as handle:
                json.dump(metadata, handle, ensure_ascii=False, indent=2)
            logger.info('Saved metadata for model %s', model_name)
            return True
        except Exception as exc:
            logger.error('Failed to save metadata for %s: %s', model_name, exc)
            return False

    def load_metadata(self, model_name: str) -> Optional[Any]:
        try:
            meta_file = self.metadata_path(model_name)
            if not meta_file.exists():
                return None
            import json

            with meta_file.open('r', encoding='utf-8') as handle:
                return json.load(handle)
        except Exception as exc:
            logger.error('Failed to load metadata for %s: %s', model_name, exc)
            return None

    def compare_performance(self, first_model: str, second_model: str) -> Dict[str, Any]:
        first_meta = self.load_metadata(first_model) or {}
        second_meta = self.load_metadata(second_model) or {}
        return {
            'first_model': first_model,
            'second_model': second_model,
            'first_accuracy': first_meta.get('accuracy'),
            'second_accuracy': second_meta.get('accuracy'),
            'difference': None if first_meta.get('accuracy') is None or second_meta.get('accuracy') is None else first_meta.get('accuracy') - second_meta.get('accuracy'),
        }
