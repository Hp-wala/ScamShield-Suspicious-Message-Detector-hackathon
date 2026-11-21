import csv
import re
import random
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SEED = 42


def normalize(text):
    text = str(text).lower()
    text = re.sub(r"\b\d+(?:[.,]\d+)*\b", "#", text)
    text = re.sub(r"[^a-z0-9#]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def near_group(text):
    words = normalize(text).split()
    return " ".join(words[:5])


def read_csv(path):
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["text", "label", "category", "channel", "lang"])
        writer.writeheader()
        writer.writerows(rows)


def print_counts(name, rows):
    print(name)
    print("  rows:", len(rows))
    print("  labels:", dict(Counter(row["label"] for row in rows)))
    print("  lang:", dict(Counter(row["lang"] for row in rows)))
    print("  channel:", dict(Counter(row["channel"] for row in rows)))
    print("  categories:", dict(Counter(row["category"] or "(genuine)" for row in rows)))


def main():
    source = DATA / "dataset.csv"
    rows = read_csv(source)
    if not rows:
        raise SystemExit("dataset.csv is empty")

    groups = defaultdict(list)
    for row in rows:
        stratum = (row["label"], row["category"])
        group_key = near_group(row["text"])
        groups[(stratum, group_key)].append(row)

    strata = defaultdict(list)
    rng = random.Random(SEED)
    for (stratum, _group), members in groups.items():
        strata[stratum].append(members)
    train = []
    test = []
    for stratum in sorted(strata):
        members = strata[stratum]
        rng.shuffle(members)
        flat_count = sum(len(group) for group in members)
        train_count = int(round(flat_count * 0.70))
        stratum_train = 0
        for group in members:
            if stratum_train < train_count:
                train.extend(group)
                stratum_train += len(group)
            else:
                test.extend(group)

    rng.shuffle(train)
    rng.shuffle(test)
    write_csv(DATA / "dataset_train.csv", train)
    write_csv(DATA / "dataset_test.csv", test)

    train_keys = {normalize(row["text"]) for row in train}
    test_keys = {normalize(row["text"]) for row in test}
    overlap = train_keys & test_keys
    if overlap:
        raise SystemExit(f"Train/test overlap detected: {len(overlap)} normalized texts")
    if len(train) + len(test) != len(rows):
        raise SystemExit("Split lost or duplicated source rows")

    print_counts("FULL", rows)
    print_counts("TRAIN", train)
    print_counts("TEST", test)
    print("zero_text_overlap:", len(overlap))


if __name__ == "__main__":
    main()
