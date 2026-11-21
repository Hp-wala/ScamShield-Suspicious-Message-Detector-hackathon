# ScamShield

ScamShield is an offline, multi-channel threat intelligence web app for suspicious SMS, WhatsApp messages, emails, and links. It uses local rule-based analysis and stores no raw message text.

## Run

```bash
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Privacy

The app performs analysis locally. SQLite reports contain only channel, category, risk score, a SHA-256 hash of normalized text, and timestamp. Raw messages are not stored or logged.
