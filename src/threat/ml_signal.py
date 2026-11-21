"""Optional lightweight text-model signal for the rule-based threat scorer."""
from .nlp import TextModel


MODEL = TextModel()


def ml_signal(text: str) -> dict | None:
    probability = MODEL.predict_proba(text)
    if probability <= 0.7:
        return None
    weight = min(20, max(1, round((probability - 0.7) / 0.3 * 20)))
    return {
        "id": "text_model",
        "label": "Similar to known scam messages (text model)",
        "category": "General",
        "weight": weight,
        "points": weight,
        "explanation": "The lightweight text model found wording patterns similar to scam examples.",
        "matches": [],
        "probability": probability,
    }
