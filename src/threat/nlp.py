"""Small pure-Python NLP preprocessing and unigram/bigram TF-IDF Naive Bayes."""
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Iterable

from src.core.validator import Validator


MODEL_PATH = Path(__file__).resolve().parent / "model.json"
URL_RE = re.compile(r"(?:https?://|hxxp://|www\.)\S+", re.I)
PHONE_RE = re.compile(r"(?<!\d)\d{10}(?!\d)")
NUMBER_RE = re.compile(r"\b\d+(?:[.,]\d+)*\b")


def remove_extra_spaces(text: str) -> str:
    if text is None:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()


def lowercase(text: str) -> str:
    return remove_extra_spaces(text).lower()


def preprocess_text(text: str) -> str:
    text = lowercase(text)
    replacements = {"<url>": "__url_token__", "<phone>": "__phone_token__", "<num>": "__num_token__"}
    for placeholder, token in replacements.items():
        text = text.replace(placeholder, token)
    text = URL_RE.sub("<url>", text)
    text = PHONE_RE.sub("<phone>", text)
    text = NUMBER_RE.sub("<num>", text)
    for placeholder, token in replacements.items():
        text = text.replace(placeholder, token)
    text = re.sub(r"[^a-z0-9_\s]", " ", text)
    text = remove_extra_spaces(text)
    for placeholder, token in replacements.items():
        text = text.replace(token, placeholder)
    return text


def sentence_tokenize(text: str) -> list[str]:
    text = remove_extra_spaces(text)
    if not text:
        return []
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]


def tokenize(text: str) -> list[str]:
    cleaned = preprocess_text(text)
    words = cleaned.split()
    features = list(words)
    features.extend(f"{words[index]}_{words[index + 1]}" for index in range(len(words) - 1))
    return features


def tokenise(text: str) -> list[str]:
    return tokenize(text)


class TextModel:
    def __init__(self, model_path: Path = MODEL_PATH) -> None:
        self.model_path = Path(model_path)
        self.model = None
        self.load()

    def load(self) -> bool:
        try:
            with self.model_path.open("r", encoding="utf-8") as handle:
                self.model = json.load(handle)
            return True
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            self.model = None
            return False

    def predict_proba(self, text: str) -> float:
        if not self.model:
            return 0.5
        features = tokenize(text)
        counts = Counter(features)
        vocab = set(self.model["idf"])
        score = float(self.model["log_priors"].get("scam", math.log(0.5)))
        weighted = self.model.get("weighted_token_counts", {}).get("scam", {})
        total_weight = sum(weighted.values()) or 1.0
        for feature, count in counts.items():
            if feature not in vocab:
                continue
            tfidf = (1.0 + math.log(count)) * float(self.model["idf"].get(feature, 1.0))
            token_log_prob = (float(weighted.get(feature, 0.0)) + 1.0) / (total_weight + len(vocab))
            score += tfidf * math.log(token_log_prob)
        other = "genuine"
        other_weighted = self.model.get("weighted_token_counts", {}).get(other, {})
        other_total = sum(other_weighted.values()) or 1.0
        other_score = float(self.model["log_priors"].get(other, math.log(0.5)))
        for feature, count in counts.items():
            if feature not in vocab:
                continue
            tfidf = (1.0 + math.log(count)) * float(self.model["idf"].get(feature, 1.0))
            token_log_prob = (float(other_weighted.get(feature, 0.0)) + 1.0) / (other_total + len(vocab))
            other_score += tfidf * math.log(token_log_prob)
        maximum = max(score, other_score)
        scam_prob = math.exp(score - maximum) / (math.exp(score - maximum) + math.exp(other_score - maximum))
        return max(0.0, min(1.0, scam_prob))


def train(rows: Iterable[dict], model_path: Path = MODEL_PATH) -> dict:
    documents = {"scam": [], "genuine": []}
    for row in rows:
        label = str(row["label"]).lower()
        if label in documents:
            documents[label].append(tokenize(str(row["text"])))
    if not documents["scam"] or not documents["genuine"]:
        raise ValueError("Both scam and genuine training rows are required")

    document_frequency = Counter()
    for label_features in documents.values():
        for features in label_features:
            document_frequency.update(set(features))
    document_count = sum(len(values) for values in documents.values())
    idf = {
        feature: round(math.log((document_count + 1.0) / (document_frequency[feature] + 1.0)) + 1.0, 6)
        for feature in document_frequency
    }
    priors = {
        label: len(values) / document_count
        for label, values in documents.items()
    }
    weighted_token_counts = {"scam": Counter(), "genuine": Counter()}
    for label, label_documents in documents.items():
        for features in label_documents:
            counts = Counter(features)
            for feature, count in counts.items():
                if feature in idf:
                    weighted_token_counts[label][feature] += (1.0 + math.log(count)) * idf[feature]
    model = {
        "version": 1,
        "idf": idf,
        "weighted_token_counts": {
            label: {feature: round(weight, 6) for feature, weight in counts.items()}
            for label, counts in weighted_token_counts.items()
        },
        "log_priors": {label: round(math.log(prior), 6) for label, prior in priors.items()},
    }
    model_path.parent.mkdir(parents=True, exist_ok=True)
    with model_path.open("w", encoding="utf-8") as handle:
        json.dump(model, handle, ensure_ascii=False, sort_keys=True)
    return model
