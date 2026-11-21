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

## Limitations

ScamShield uses explainable heuristics, not a guarantee. URL and message results can have false positives or miss novel scams. For money loss or threats, call 1930 or visit `cybercrime.gov.in`.
