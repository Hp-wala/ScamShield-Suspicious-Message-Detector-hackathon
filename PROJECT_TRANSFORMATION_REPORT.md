# ScamShield Project Report

## 1. Project Overview

ScamShield is a Flask web application for detecting and explaining potential fraud in SMS, WhatsApp messages, emails and suspicious URLs. It focuses on Indian-context scams and English/Hinglish warning signs.

## 2. Architecture

```text
+-----------------------+
| Message / Link Input  |
+-----------+-----------+
            |
            v
+-----------------------+
| Channel Adapter       |
+-----------+-----------+
            |
            v
+-----------------------+
| Normalize and Extract |
+-----------+-----------+
            |
            v
+-----------------------+
| Rules, URL Checks,    |
| and Text Model        |
+-----------+-----------+
            |
            v
+-----------------------+
| Risk Score, Verdict,  |
| Reasons, and Advice   |
+-----------------------+
```

## 3. Application Components

- `app.py` — Flask application, static frontend delivery, analysis/reporting APIs, validation, rate limiting and security headers.
- `src/threat/engine.py` — threat-analysis orchestration.
- `src/threat/rules.py` — English and Hinglish scam indicators and safeguards.
- `src/threat/urls.py` — URL extraction and suspicious-link checks.
- `src/threat/adapters.py` — SMS, WhatsApp, email and URL input handling.
- `src/threat/pipeline.py` — staged message-analysis pipeline.
- `src/report_store.py` — SQLite reporting and dashboard statistics.
- `web/` — responsive analyzer, dashboard and scam-awareness interface.
- `tests/` — automated engine, adapter, API, privacy and security tests.

## 4. User Features

- Analyze SMS, WhatsApp messages, email content and suspicious links.
- Review a WhatsApp text export message by message.
- See a risk score, verdict, warning signs and safety advice.
- Scan images for text or QR links when OCR/QR system support is installed.
- Analyze pasted call transcripts.
- View report statistics, channel/category breakdowns, timeline and available state reports.
- Explore scam examples, safety rules and an awareness quiz.
- Access Indian reporting guidance, including helpline 1930.

## 5. Privacy and Safety

- Raw message text is not stored in report records or logged by the analysis flow.
- SQLite reports store channel, category, risk score, normalized-text SHA-256 hash and timestamp.
- Core message analysis is local. Optional reputation and breach checks may make network requests when configured.
- Results are heuristic guidance and are not a guarantee of real-world accuracy.

## 6. Testing and Deployment

Run the test suite with:

```bash
python -m pytest -q
```

Render uses the configuration in `render.yaml`:

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`

Live application: https://scamshield-suspicious-message-detector.onrender.com

On Render's free tier, the service may sleep when idle and local SQLite data may reset.
