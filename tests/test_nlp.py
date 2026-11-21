import csv
from pathlib import Path

from src.threat.nlp import (
    TextModel,
    lowercase,
    preprocess_text,
    remove_extra_spaces,
    sentence_tokenize,
    tokenize,
)


ROOT = Path(__file__).resolve().parents[1]


def test_nlp_wrappers():
    assert lowercase("  HELLO   world ") == "hello world"
    assert remove_extra_spaces("  one\t two\nthree ") == "one two three"
    assert len(sentence_tokenize("First. Second? Third")) == 3


def test_normalization_placeholders():
    text = "Call 9876543210 at https://example.com now 250"
    cleaned = preprocess_text(text)
    assert "<phone>" in cleaned
    assert "<url>" in cleaned
    assert "<num>" in cleaned
    assert set(tokenize(cleaned)).issuperset({"<phone>", "<url>"})


def test_dataset_shape_and_split():
    with (ROOT / "data" / "dataset.csv").open("r", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 200
    assert sum(row["label"] == "scam" for row in rows) == 110
    assert sum(row["label"] == "genuine" for row in rows) == 90
    assert sum(row["lang"] == "hinglish" for row in rows) >= 40
    for path, expected in (
        (ROOT / "data" / "dataset_train.csv", 140),
        (ROOT / "data" / "dataset_test.csv", 60),
    ):
        with path.open("r", encoding="utf-8") as handle:
            split_rows = list(csv.DictReader(handle))
        assert len(split_rows) == expected


def test_model_loads_and_probability_range():
    model_path = ROOT / "src" / "threat" / "model.json"
    if not model_path.exists():
        assert TextModel(model_path).predict_proba("Hello") == 0.5
    else:
        probability = TextModel(model_path).predict_proba(
            "Account blocked. Share OTP and KYC immediately."
        )
        assert 0.0 <= probability <= 1.0
