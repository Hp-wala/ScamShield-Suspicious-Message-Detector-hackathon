# ScamShield Implementation Audit

## Project Scope

ScamShield is a Flask web application for assessing potentially fraudulent SMS messages, WhatsApp messages, emails and suspicious links. Its core threat analysis focuses on Indian-context scams and English/Hinglish indicators.

## Application Structure

| Component | Responsibility |
|---|---|
| `app.py` | Serves the web application and JSON endpoints for analysis, reporting, statistics and optional checks |
| `src/threat/` | Message normalization, channel adapters, scam indicators, URL analysis, scoring and safety advice |
| `src/core/` | Configuration, validation, metadata-only logging and feedback handling |
| `src/report_store.py` | SQLite storage for privacy-safe reports and dashboard statistics |
| `web/` | Static HTML, CSS and JavaScript for analysis, dashboard and awareness tools |
| `tests/` | Automated tests for threat analysis, adapters, APIs, privacy and security behavior |

## Privacy and Security

- Raw message text is not stored in reports or logged by the analysis flow.
- Report records contain the channel, category, risk score, normalized-text SHA-256 hash and timestamp.
- API input validation, request-size limits, rate limiting, security headers and parameterized SQLite queries are implemented.
- Core message analysis runs locally. Optional reputation and breach checks may contact external services when enabled.

## Optional Capabilities

- Screenshot OCR and QR decoding depend on the corresponding system libraries being available.
- Safe Browsing, VirusTotal and email breach checks require configuration and network access.
- Call transcripts can be analyzed as text; WAV transcription is not implemented end-to-end.

## Deployment

Render configuration is provided in `render.yaml`. The deployed application is available at:

https://scamshield-suspicious-message-detector.onrender.com

The Render free tier may sleep while idle, and its local SQLite files may reset.
