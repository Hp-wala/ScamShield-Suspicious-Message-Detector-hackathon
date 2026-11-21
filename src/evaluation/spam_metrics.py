from dataclasses import dataclass
from typing import Dict, Any

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix


@dataclass
class SpamMetrics:
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float | None
    confusion_matrix: tuple


class MetricsCalculator:
    @staticmethod
    def calculate(y_true, y_pred, y_prob=None) -> SpamMetrics:
        if not y_true:
            return SpamMetrics(
                accuracy=0.0,
                precision=0.0,
                recall=0.0,
                f1_score=0.0,
                roc_auc=None,
                confusion_matrix=((0, 0), (0, 0)),
            )

        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        roc_auc = None

        if y_prob is not None:
            try:
                roc_auc = roc_auc_score(y_true, y_prob)
            except Exception:
                roc_auc = None

        cm = confusion_matrix(y_true, y_pred)

        return SpamMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            roc_auc=roc_auc,
            confusion_matrix=tuple(map(tuple, cm)),
        )

    @staticmethod
    def to_dict(metrics: SpamMetrics) -> Dict[str, Any]:
        return {
            'accuracy': metrics.accuracy,
            'precision': metrics.precision,
            'recall': metrics.recall,
            'f1_score': metrics.f1_score,
            'roc_auc': metrics.roc_auc,
            'confusion_matrix': metrics.confusion_matrix,
        }
