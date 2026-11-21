from pathlib import Path

from src.threat.nlp import TextModel, lowercase, preprocess_text, remove_extra_spaces, sentence_tokenize, tokenise, train


ROOT = Path(__file__).resolve().parents[1]


def test_named_nlp_stages():
    assert lowercase("  HELLO   WORLD ") == "hello world"
    assert remove_extra_spaces("one \n  two") == "one two"
    assert sentence_tokenize("First. Second? Third") == ["First.", "Second?", "Third"]


def test_preprocess_placeholders_and_tokenise():
    cleaned = preprocess_text("Call 0000000000 at https://example.com now 250")
    assert "<phone>" in cleaned
    assert "<url>" in cleaned
    assert "<num>" in cleaned
    features = tokenise(cleaned)
    assert "<phone>" in features
    assert "<url>" in features
    assert "<num>" in features


def test_train_predict_tiny_inline_sample(tmp_path):
    rows = [
        {"text": "Your account is blocked. Share OTP immediately.", "label": "scam"},
        {"text": "Update KYC and pay fee through this link.", "label": "scam"},
        {"text": "Do not share this OTP. Bank support is never asking.", "label": "genuine"},
        {"text": "Your lunch meeting is at 6 pm tomorrow.", "label": "genuine"},
    ]
    model_path = tmp_path / "model.json"
    train(rows, model_path)
    model = TextModel(model_path)
    assert 0.0 <= model.predict_proba("Share OTP and blocked account") <= 1.0


def test_missing_model_degrades_gracefully(tmp_path):
    model = TextModel(tmp_path / "missing.json")
    assert model.predict_proba("Account blocked OTP") == 0.5
