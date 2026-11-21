import csv
import sys
from pathlib import Path

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
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
    }


def predicted_label(result):
    return "scam" if result["verdict"] in {"Likely Scam", "Suspicious"} else "genuine"


def main():
    test_rows = load_rows(ROOT / "data" / "dataset_test.csv")
    engine = ThreatEngine()
    rules_true, rules_pred = [], []
    full_true, full_pred = [], []
    misclassified = []

    for row in test_rows:
        true = row["label"]
        rules_result = score_message(row["channel"], row["text"], use_ml=False)
        full_result = engine.analyze(row["text"], row["channel"])
        rules_label = predicted_label(rules_result)
        full_label = predicted_label(full_result)
        rules_true.append(true)
        rules_pred.append(rules_label)
        full_true.append(true)
        full_pred.append(full_label)
        if full_label != true:
            misclassified.append({
                "text": row["text"],
                "label": true,
                "predicted": full_label,
                "score": full_result["score"],
                "category": full_result["category"],
            })

    rules_metrics = metrics(rules_true, rules_pred)
    full_metrics = metrics(full_true, full_pred)

    lines = [
        "# Dataset and Evaluation",
        "",
        "Synthetic, fully local Phase 8 evaluation.",
        "",
        "## Dataset",
        "",
        f"- Full dataset: {len(load_rows(ROOT / 'data' / 'dataset.csv'))} rows",
        f"- Train: {len(load_rows(ROOT / 'data' / 'dataset_train.csv'))} rows",
        f"- Test: {len(test_rows)} rows",
        "- Split: deterministic 70/30 stratified by label, fixed seed 20260314.",
        "- The test split was not used to tune rule weights.",
        "",
        "## Rules-only",
        "",
        f"- Accuracy: {rules_metrics['accuracy']:.3f}",
        f"- Precision: {rules_metrics['precision']:.3f}",
        f"- Recall: {rules_metrics['recall']:.3f}",
        f"- F1: {rules_metrics['f1']:.3f}",
        f"- Confusion matrix: TP={rules_metrics['tp']} TN={rules_metrics['tn']} FP={rules_metrics['fp']} FN={rules_metrics['fn']}",
        "",
        "## Rules + lightweight text model",
        "",
        f"- Accuracy: {full_metrics['accuracy']:.3f}",
        f"- Precision: {full_metrics['precision']:.3f}",
        f"- Recall: {full_metrics['recall']:.3f}",
        f"- F1: {full_metrics['f1']:.3f}",
        f"- Confusion matrix: TP={full_metrics['tp']} TN={full_metrics['tn']} FP={full_metrics['fp']} FN={full_metrics['fn']}",
        "",
        "## Misclassified messages",
        "",
    ]
    if misclassified:
        for item in misclassified:
            lines.append(
                f"- `{item['text']}` | expected={item['label']} | predicted={item['predicted']} "
                f"| score={item['score']} | category={item['category']}"
            )
    else:
        lines.append("- None")

    lines.extend([
        "",
        "## Limitations",
        "",
        "- This dataset is synthetic and should not be treated as real-world prevalence evidence.",
        "- The text model is a lightweight unigram/bigram multinomial Naive Bayes model; it is not a transformer.",
        "- Rule signals remain primary, and the ML signal cannot promote a message to Likely Scam by itself.",
    ])

    output = "\n".join(lines) + "\n"
    print(output)
    (ROOT / "EVAL.md").write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
