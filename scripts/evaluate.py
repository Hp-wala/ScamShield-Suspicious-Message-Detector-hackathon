import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.threat.engine import ThreatEngine
from src.threat.scorer import score_message


def load_rows(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def metrics(y_true, y_pred):
    tp = sum(t == "scam" and p == "scam" for t, p in zip(y_true, y_pred))
    tn = sum(t == "genuine" and p == "genuine" for t, p in zip(y_true, y_pred))
    fp = sum(t == "genuine" and p == "scam" for t, p in zip(y_true, y_pred))
    fn = sum(t == "scam" and p == "genuine" for t, p in zip(y_true, y_pred))
    accuracy = (tp + tn) / len(y_true) if y_true else 0.0
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    false_positive_rate = fp / (fp + tn) if fp + tn else 0.0
    false_negative_rate = fn / (fn + tp) if fn + tp else 0.0
    return {
        "accuracy": round(accuracy, 6),
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round(f1, 6),
        "false_positive_rate": round(false_positive_rate, 6),
        "false_negative_rate": round(false_negative_rate, 6),
        "confusion_matrix": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
    }


def predicted_label(result, strict=False):
    if result["verdict"] == "Likely Scam":
        return "scam"
    if not strict and result["verdict"] == "Suspicious":
        return "scam"
    return "genuine"


def grouped_accuracy(rows, key_name, predictions):
    grouped = defaultdict(list)
    for row, prediction in zip(rows, predictions):
        grouped[row[key_name] or "(genuine)"].append(prediction == row["label"])
    return {key: round(sum(values) / len(values), 6) for key, values in sorted(grouped.items())}


def per_category_recall(rows, predictions):
    grouped = defaultdict(lambda: {"tp": 0, "fn": 0})
    for row, prediction in zip(rows, predictions):
        if row["label"] != "scam":
            continue
        category = row["category"] or "Other"
        if prediction == "scam":
            grouped[category]["tp"] += 1
        else:
            grouped[category]["fn"] += 1
    return {
        category: round(values["tp"] / (values["tp"] + values["fn"]), 6)
        if values["tp"] + values["fn"] else 0.0
        for category, values in sorted(grouped.items())
    }


def average_scores(rows, scores):
    scam = [score for row, score in zip(rows, scores) if row["label"] == "scam"]
    genuine = [score for row, score in zip(rows, scores) if row["label"] == "genuine"]
    return {
        "scam": round(sum(scam) / len(scam), 6) if scam else 0.0,
        "genuine": round(sum(genuine) / len(genuine), 6) if genuine else 0.0,
    }


def main():
    train_rows = load_rows(ROOT / "data" / "dataset_train.csv")
    test_rows = load_rows(ROOT / "data" / "dataset_test.csv")
    engine = ThreatEngine()

    rules_flexible = []
    rules_strict = []
    full_flexible = []
    full_strict = []
    full_results = []

    for row in test_rows:
        rules_result = score_message(row["channel"], row["text"], use_ml=False)
        full_result = engine.analyze(row["text"], row["channel"])
        full_results.append(full_result)
        rules_flexible.append(predicted_label(rules_result, strict=False))
        rules_strict.append(predicted_label(rules_result, strict=True))
        full_flexible.append(predicted_label(full_result, strict=False))
        full_strict.append(predicted_label(full_result, strict=True))

    true_labels = [row["label"] for row in test_rows]
    rules_flex_metrics = metrics(true_labels, rules_flexible)
    rules_strict_metrics = metrics(true_labels, rules_strict)
    full_flex_metrics = metrics(true_labels, full_flexible)
    full_strict_metrics = metrics(true_labels, full_strict)

    full_flex_metrics["per_category_recall"] = per_category_recall(test_rows, full_flexible)
    full_flex_metrics["per_language_accuracy"] = grouped_accuracy(test_rows, "lang", full_flexible)
    full_flex_metrics["per_channel_accuracy"] = grouped_accuracy(test_rows, "channel", full_flexible)
    full_flex_metrics["average_score"] = average_scores(test_rows, [item["score"] for item in full_results])

    class_counts = {
        "scam": sum(row["label"] == "scam" for row in test_rows),
        "genuine": sum(row["label"] == "genuine" for row in test_rows),
    }
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "train_size": len(train_rows),
        "test_size": len(test_rows),
        "class_counts": class_counts,
        "dataset_notice": "Synthetic dataset - not real-world accuracy",
        "rules_only": {
            "flexible": rules_flex_metrics,
            "strict": rules_strict_metrics,
        },
        "rules_plus_ml": {
            "flexible": full_flex_metrics,
            "strict": full_strict_metrics,
        },
        "misclassified_count": sum(prediction != row["label"] for row, prediction in zip(test_rows, full_flexible)),
    }
    (ROOT / "data" / "eval_results.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    misclassified = []
    for row, prediction, result in zip(test_rows, full_flexible, full_results):
        if prediction != row["label"]:
            misclassified.append(
                f"- `{row['text']}` | expected={row['label']} | predicted={prediction} "
                f"| score={result['score']} | category={row['category'] or '(genuine)'}"
            )

    lines = [
        "# Dataset and Evaluation",
        "",
        "Synthetic dataset - not real-world accuracy",
        "",
        "## Dataset and split",
        "",
        f"- Full: {len(load_rows(ROOT / 'data' / 'dataset.csv'))}",
        f"- Train: {len(train_rows)}",
        f"- Test: {len(test_rows)}",
        "- Seed: 42",
        "- Stratified by label and category with near-duplicate groups kept together.",
        "",
        "## Flexible view",
        "",
        "| Metric | Rules-only | Rules + ML |",
        "|---|---:|---:|",
        "| Accuracy | %.3f | %.3f |" % (rules_flex_metrics["accuracy"], full_flex_metrics["accuracy"]),
        "| Precision | %.3f | %.3f |" % (rules_flex_metrics["precision"], full_flex_metrics["precision"]),
        "| Recall | %.3f | %.3f |" % (rules_flex_metrics["recall"], full_flex_metrics["recall"]),
        "| F1 | %.3f | %.3f |" % (rules_flex_metrics["f1"], full_flex_metrics["f1"]),
        "| False-positive rate | %.3f | %.3f |" % (rules_flex_metrics["false_positive_rate"], full_flex_metrics["false_positive_rate"]),
        "| False-negative rate | %.3f | %.3f |" % (rules_flex_metrics["false_negative_rate"], full_flex_metrics["false_negative_rate"]),
        "",
        "Rules-only confusion: `TP={tp}, FP={fp}, TN={tn}, FN={fn}`".format(**rules_flex_metrics["confusion_matrix"]),
        "Rules + ML confusion: `TP={tp}, FP={fp}, TN={tn}, FN={fn}`".format(**full_flex_metrics["confusion_matrix"]),
        "",
        "## Strict view (Likely Scam only)",
        "",
        "| Metric | Rules-only | Rules + ML |",
        "|---|---:|---:|",
        "| Accuracy | %.3f | %.3f |" % (rules_strict_metrics["accuracy"], full_strict_metrics["accuracy"]),
        "| Precision | %.3f | %.3f |" % (rules_strict_metrics["precision"], full_strict_metrics["precision"]),
        "| Recall | %.3f | %.3f |" % (rules_strict_metrics["recall"], full_strict_metrics["recall"]),
        "| F1 | %.3f | %.3f |" % (rules_strict_metrics["f1"], full_strict_metrics["f1"]),
        "| False-positive rate | %.3f | %.3f |" % (rules_strict_metrics["false_positive_rate"], full_strict_metrics["false_positive_rate"]),
        "| False-negative rate | %.3f | %.3f |" % (rules_strict_metrics["false_negative_rate"], full_strict_metrics["false_negative_rate"]),
        "",
        "## Per-category recall",
        "",
    ]
    for category, recall in full_flex_metrics["per_category_recall"].items():
        lines.append(f"- {category}: {recall:.3f}")
    lines.extend(["", "## Per-language accuracy", ""])
    for lang, accuracy in full_flex_metrics["per_language_accuracy"].items():
        lines.append(f"- {lang}: {accuracy:.3f}")
    lines.extend(["", "## Per-channel accuracy", ""])
    for channel, accuracy in full_flex_metrics["per_channel_accuracy"].items():
        lines.append(f"- {channel}: {accuracy:.3f}")
    lines.extend([
        "",
        "## Average score",
        "",
        f"- Scam: {full_flex_metrics['average_score']['scam']:.3f}",
        f"- Genuine: {full_flex_metrics['average_score']['genuine']:.3f}",
        "",
        "## Misclassified test messages",
        "",
    ])
    lines.extend(misclassified or ["- None"])
    lines.extend([
        "",
        "## Limitations",
        "",
        "- Synthetic data does not represent real-world scam prevalence.",
        "- The test set is small and Hinglish coverage is limited.",
        "- Rules and the lightweight text model can both be evaded.",
    ])

    (ROOT / "EVAL.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
