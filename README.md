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

Phase 8 includes a fully synthetic CSV dataset of 200 messages: 110 scam and 90 genuine, with English and Hinglish examples across bank/KYC, delivery, government, prizes, jobs, UPI, utility, investment, digital-arrest and impersonation categories. No real phone numbers, names or personal data are included.

The fixed split is 70% train and 30% test, stratified by label with seed `20260314`. The test split is not used to tune rule weights.

The local text model is a pure-Python unigram/bigram TF-IDF-style multinomial Naive Bayes classifier. It is stored at `src/threat/model.json` and remains a secondary signal: rules stay primary, and the model cannot promote a message to Likely Scam by itself.

Retrain and evaluate:

```bash
python scripts/train_model.py
python scripts/evaluate.py
```

The latest test metrics and misclassified examples are recorded in `EVAL.md`. Synthetic benchmark results are not a claim of real-world accuracy.

## Limitations

ScamShield uses explainable heuristics, not a guarantee. URL and message results can have false positives or miss novel scams. For money loss or threats, call 1930 or visit `cybercrime.gov.in`.
