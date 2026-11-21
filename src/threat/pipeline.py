"""Small staged pipeline adapted from the legacy extraction pipeline pattern."""
from .normalize import clean_text
from .adapters import registry


def analyze(channel: str, raw: str, sender: str | None = None):
    adapter = registry.get(channel)
    extracted = adapter.extract(raw, sender=sender)
    if extracted.get("type") == "chat":
        return extracted, ""
    normalized = clean_text(extracted["text"])
    return extracted, normalized
