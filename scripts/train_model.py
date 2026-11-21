import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.threat.nlp import TextModel, train


def load_rows(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


if __name__ == "__main__":
    train_path = ROOT / "data" / "dataset_train.csv"
    rows = load_rows(train_path)
    model = train(rows)
    model_path = ROOT / "src" / "threat" / "model.json"
    print(f"trained_rows={len(rows)} model={model_path} size={model_path.stat().st_size} bytes")
    print(f"vocabulary={len(model['idf'])}")
    loaded = TextModel(model_path)
    print(f"load={loaded.model is not None}")
