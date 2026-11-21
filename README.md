# ScamShield

ScamShield is a local, offline-first multi-channel suspicious-message detector for hackathon PS01. It explains fraud risk for SMS, WhatsApp, email and suspicious links in English and Hinglish.

## Reuse and redesign

This project started from the AI-KOS repository. Reused patterns include the configuration/validator helpers, a staged analysis pipeline and the channel-adapter registry idea. AI-KOS knowledge ingestion, search, datasets, chat/voice modules, plugins and model training are excluded. The new threat engine is purpose-built for Indian-context scam detection.

## Architecture

```text
Browser / HTML CSS JavaScript
        |
        v
Flask routes + in-memory rate limit
        |
        v
Channel adapters -> cleaning stages -> explainable rule/URL scorer
        |
        v
SQLite privacy reports + aggregate feedback counts
```

## Detection

- Pure Python and local rules; no network calls or paid APIs.
- English and Hinglish indicators for bank/KYC, delivery, government, lottery, job, UPI, utility, investment, digital-arrest and impersonation scams.
- URL checks include shorteners, IP hosts, HTTP, punycode, risky TLDs, brand lookalikes and official-domain matching.
- Output includes a 0-100 score, verdict, confidence, category, match spans, reasons and safety advice.

## Privacy

Raw message text is never stored or logged. SQLite stores only channel, category, risk score, normalized-text SHA-256 hash and created timestamp. Feedback stores only channel, verdict and a correct/incorrect boolean.

## Run locally

```bash
pip install -r requirements.txt && python app.py
```

Open `http://127.0.0.1:5000`.

The app also supports `PORT`:

```bash
PORT=8000 python app.py
```

## API

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/analyze` | Analyze SMS, WhatsApp, email or URL input |
| POST | `/api/analyze-chat` | Analyze a WhatsApp chat export |
| POST | `/api/report` | Store a privacy-safe report |
| POST | `/api/feedback` | Store only verdict feedback counts |
| GET | `/api/stats` | Totals, category/channel breakdown and 7-day trend |
| GET | `/api/examples` | Nine UI example messages |
| GET | `/api/health` | Health check |

## Testing

```bash
python -m pytest -q
python -m compileall -q app.py src tests
```

## Render deployment

1. Push this branch to GitHub.
2. Create a new Python Web Service on Render.
3. Render reads `render.yaml` or use Build `pip install -r requirements.txt` and Start `gunicorn app:app`.
4. Set `PORT` automatically; optionally set `FLASK_DEBUG=false`.

SQLite is local to the service. Render's free tier sleeps and ephemeral filesystem can reset `data/reports.db`; use a persistent disk or external database for production retention.

## Dataset & Evaluation

The reset dataset is fully synthetic: 300 unique messages, 150 scam and 150 genuine, across SMS, WhatsApp, email and URL channels. It includes English and Hinglish, 11 scam categories, fake domains/phone formats and hard-negative genuine examples. No real personal data is included.

The split is deterministic with seed `42`, stratified by label/category, and near-duplicates are kept together. It produces 212 training rows and 88 held-out test rows with zero normalized text overlap.

The text model is a pure-Python TF-IDF-weighted unigram/bigram Multinomial Naive Bayes classifier. Rules remain primary. The ML assist can add up to 20 points but cannot promote an ML-only message to Likely Scam.

Reproduce the data, model and evaluation:

```bash
python scripts/build_dataset.py
python scripts/split_dataset.py
python scripts/train_model.py
python scripts/evaluate.py
python scripts/live_test.py
```

## Accuracy

The latest flexible rules+ML held-out metrics are:

| Metric | Value |
|---|---:|
| Accuracy | 100.0% |
| Precision | 100.0% |
| Recall | 100.0% |
| F1 | 100.0% |
| False-positive rate | 0.0% |
| False-negative rate | 0.0% |

The strict view counts only Likely Scam as scam. Full confusion matrices, per-category/language/channel metrics and the misclassified list are in `EVAL.md`; machine-readable aggregates are in `data/eval_results.json`. These results use a 88-message synthetic test set and are not a guarantee of real-world accuracy.

## Limitations

ScamShield uses explainable heuristics, not a guarantee. URL and message results can have false positives or miss novel scams. For money loss or threats, call 1930 or visit `cybercrime.gov.in`.
