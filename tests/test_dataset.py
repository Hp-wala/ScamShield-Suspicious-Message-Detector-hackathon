import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
VALID_LABELS = {"scam", "genuine"}
VALID_CATEGORIES = {
    "", "Bank/KYC", "Delivery", "Government", "Lottery/Prize",
    "Job/Work-from-home", "UPI/Payment", "Electricity/Utility",
    "Investment", "Impersonation", "Digital Arrest", "Other",
}


def normalize(text):
    text = str(text).lower()
    text = re.sub(r"\b\d+(?:[.,]\d+)*\b", "#", text)
    text = re.sub(r"[^a-z0-9#]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def read_csv(path):
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_dataset_is_unique_balanced_and_valid():
    rows = read_csv(DATA / "dataset.csv")
    assert len(rows) >= 300
    assert sum(row["label"] == "scam" for row in rows) >= 150
    assert sum(row["label"] == "genuine" for row in rows) >= 150
    keys = [normalize(row["text"]) for row in rows]
    assert len(keys) == len(set(keys))
    for row in rows:
        assert row["label"] in VALID_LABELS
        assert row["category"] in VALID_CATEGORIES
        assert row["channel"] in {"sms", "whatsapp", "email", "url"}
        assert row["lang"] in {"en", "hinglish"}
        if row["label"] == "genuine":
            assert row["category"] == ""


def test_train_test_no_overlap_and_near_duplicate_guard():
    full = read_csv(DATA / "dataset.csv")
    train = read_csv(DATA / "dataset_train.csv")
    test = read_csv(DATA / "dataset_test.csv")
    train_keys = {normalize(row["text"]) for row in train}
    test_keys = {normalize(row["text"]) for row in test}
    assert not (train_keys & test_keys)
    assert len(train) + len(test) == len(full)
    assert abs(len(train) / len(full) - 0.70) < 0.05


def test_no_real_phone_like_personal_data():
    rows = read_csv(DATA / "dataset.csv")
    suspicious = re.compile(r"(?<!\d)(?:[6-9]\d{9}|[987]\d{4}-\d{5})(?!\d)")
    for row in rows:
        assert not suspicious.search(row["text"])
