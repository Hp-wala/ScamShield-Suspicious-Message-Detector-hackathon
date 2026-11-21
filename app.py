import os
import time
from collections import defaultdict, deque
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from src.core.config_manager import ConfigManager
from src.core.feedback import FeedbackStore
from src.core.validator import Validator
from src.report_store import ReportStore
from src.threat.engine import ThreatEngine


EXAMPLES = [
    {"label": "Bank KYC SMS", "channel": "sms", "text": "Aapka SBI account blocked hai. KYC turant verify karein aur OTP share karein: http://192.168.1.20/verify"},
    {"label": "Delivery fee", "channel": "sms", "text": "Your parcel is on hold. Pay Rs 150 redelivery fee: http://bit.ly/delivery"},
    {"label": "Electricity cut-off", "channel": "sms", "text": "Bijli bill unpaid hai. Electricity disconnect tonight. Pay immediately."},
    {"label": "Lottery prize", "channel": "sms", "text": "Congratulations! You won Rs 25 lakh lucky draw. Pay Rs 500 processing fee to claim."},
    {"label": "WhatsApp job", "channel": "whatsapp", "text": "Ghar baithe earn Rs 3000 daily. No experience needed. Join Telegram and pay registration fee."},
    {"label": "UPI collect", "channel": "sms", "text": "UPI collect request for Rs 5000. Accept request to receive money. Share UPI PIN."},
    {"label": "Digital arrest", "channel": "whatsapp", "text": "You are under digital arrest. Stay on video call and do not tell anyone. Pay security fine."},
    {"label": "Genuine OTP warning", "channel": "sms", "text": "Do not share this OTP. Your bank never asks for OTP, PIN or CVV."},
    {"label": "Genuine order shipped", "channel": "sms", "text": "Your Amazon order was shipped and will be delivered tomorrow. Track at amazon.in."},
]


def create_app(config=None):
    app = Flask(__name__, template_folder="web", static_folder="web", static_url_path="/static")
    settings = config or {}
    app.config.update(settings)

    config_manager = ConfigManager()
    database_path = Path(app.config.get("DATABASE_PATH", config_manager.get("database_path")))
    reports = ReportStore(database_path)
    feedback = FeedbackStore(database_path)
    engine = ThreatEngine()
    request_windows = defaultdict(deque)

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:"
        return response

    @app.before_request
    def rate_limit():
        if not request.path.startswith("/api/"):
            return None
        ip = request.remote_addr or "unknown"
        now = time.monotonic()
        window = request_windows[ip]
        while window and now - window[0] > 60:
            window.popleft()
        if len(window) >= 60:
            return jsonify({"error": "Rate limit exceeded"}), 429
        window.append(now)
        return None

    @app.get("/")
    def index():
        return render_template("index.html")

    def analyze_payload(payload):
        channel = str(payload.get("channel", "sms")).strip().lower()
        if channel not in {"sms", "whatsapp", "email", "url"}:
            return None, jsonify({"error": "Invalid channel"}), 400
        text = payload.get("text")
        if not isinstance(text, str) or not Validator.is_valid_string(text):
            return None, jsonify({"error": "Message text is required"}), 400
        max_chars = 300000 if channel == "whatsapp" else 5000
        if len(text) > max_chars:
            return None, jsonify({"error": f"Message text exceeds {max_chars} characters"}), 413
        if channel == "whatsapp" and ("\n" in text or re_chat_marker(text)):
            result = engine.analyze_chat(text)
        elif channel == "email":
            result = engine.analyze_email(text)
        elif channel == "url":
            bare = text.strip()
            result = engine.analyze(bare, "url")
        else:
            result = engine.analyze(text, channel, sender=str(payload.get("sender", "")))
        return result, None, None

    def re_chat_marker(text):
        import re
        return bool(re.search(r"\d{1,2}/\d{1,2}/\d{2,4}.+\d{1,2}:\d{2}", text) or
                    re.search(r"\[\d{1,2}/\d{1,2}/\d{4}", text))

    @app.post("/api/analyze")
    @app.post("/api/analyze-chat")
    def analyze():
        payload = request.get_json(silent=True) or {}
        result, error, status = analyze_payload(payload)
        if error:
            return error, status
        if isinstance(result, dict) and result.get("type") == "chat":
            for message in result["messages"]:
                analysis = message["result"]
                reports.add({
                    "channel": "whatsapp",
                    "category": analysis["category"],
                    "risk_score": analysis["score"],
                    "text_hash": Validator.message_hash(analysis["text"]),
                })
        else:
            reports.add({
                "channel": payload.get("channel", "sms"),
                "category": result["category"],
                "risk_score": result["score"],
                "text_hash": Validator.message_hash(result["text"]),
            })
        return jsonify(result)

    @app.post("/api/report")
    def report():
        payload = request.get_json(silent=True) or {}
        channel = str(payload.get("channel", "")).strip().lower()
        category = str(payload.get("category", "Other")).strip()[:80]
        try:
            risk_score = int(payload["risk_score"])
        except (KeyError, TypeError, ValueError):
            return jsonify({"error": "risk_score is required"}), 400
        if channel not in {"sms", "whatsapp", "email", "url"}:
            return jsonify({"error": "Invalid channel"}), 400
        risk_score = max(0, min(100, risk_score))
        text_hash = payload.get("message_hash")
        if not text_hash:
            text = payload.get("text")
            if not isinstance(text, str):
                return jsonify({"error": "message_hash or text is required"}), 400
            text_hash = Validator.message_hash(text)
        if not isinstance(text_hash, str) or len(text_hash) != 64:
            return jsonify({"error": "Invalid message hash"}), 400
        report_id = reports.add({
            "channel": channel, "category": category,
            "risk_score": risk_score, "text_hash": text_hash,
        })
        if report_id < 0:
            return jsonify({"status": "duplicate"}), 200
        return jsonify({"status": "created", "id": report_id}), 201

    @app.post("/api/feedback")
    def add_feedback():
        payload = request.get_json(silent=True) or {}
        channel = str(payload.get("channel", "")).strip().lower()
        verdict = str(payload.get("verdict", "")).strip()[:40]
        correct = payload.get("correct")
        if channel not in {"sms", "whatsapp", "email", "url"} or not verdict or not isinstance(correct, bool):
            return jsonify({"error": "channel, verdict and correct are required"}), 400
        feedback.add(channel, verdict, correct)
        return jsonify({"status": "recorded"})

    @app.get("/api/stats")
    def stats():
        return jsonify(reports.stats())

    @app.get("/api/examples")
    def examples():
        return jsonify({"examples": EXAMPLES})

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "ScamShield"})

    @app.get("/api/reports")
    def report_list():
        return jsonify({"reports": reports.recent()})

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(413)
    def too_large(_error):
        return jsonify({"error": "Payload too large"}), 413

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=ConfigManager().get("debug", False))
