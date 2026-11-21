import json
import subprocess
import sys
from pathlib import Path

from app import create_app


ROOT = Path(__file__).resolve().parents[1]


def test_metrics_api_shape_and_privacy(tmp_path):
    app = create_app({"TESTING": True, "DATABASE_PATH": tmp_path / "test.db"})
    client = app.test_client()
    response = client.get("/api/metrics")
    assert response.status_code == 200
    payload = response.get_json()
    assert "rules_plus_ml" in payload or payload == {"available": False}
    if "rules_plus_ml" in payload:
        metrics = payload["rules_plus_ml"]["flexible"]
        for key in (
            "accuracy", "precision", "recall", "f1",
            "false_positive_rate", "false_negative_rate",
        ):
            assert 0.0 <= metrics[key] <= 1.0
        serialized = json.dumps(payload)
        assert "text:" not in serialized.lower()
        assert "misclassified" not in serialized.lower() or payload["misclassified_count"] >= 0


def test_evaluate_script_writes_valid_json(tmp_path):
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "evaluate.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert completed.returncode == 0
    with (ROOT / "data" / "eval_results.json").open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    assert payload["train_size"] + payload["test_size"] >= 300
    assert payload["dataset_notice"] == "Synthetic dataset - not real-world accuracy"
    assert 0.0 <= payload["rules_plus_ml"]["flexible"]["accuracy"] <= 1.0
