from flask import Flask, jsonify, render_template, request

from src.core.config_manager import ConfigManager
from src.core.validator import Validator
from src.report_store import ReportStore
from src.threat.engine import ThreatEngine


def create_app(config=None):
    app = Flask(__name__, template_folder="web", static_folder="web", static_url_path="/static")
    settings = config or {}
    app.config.update(settings)

    config_manager = ConfigManager()
    database_path = app.config.get("DATABASE_PATH", config_manager.get("database_path"))
    reports = ReportStore(database_path)
    engine = ThreatEngine()

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/api/analyze")
    def analyze():
        payload = request.get_json(silent=True) or {}
        channel = str(payload.get("channel", "sms")).strip().lower()
        if channel not in {"sms", "whatsapp", "email", "url"}:
            return jsonify({"error": "Invalid channel"}), 400
        text = payload.get("text")
        if not isinstance(text, str) or not Validator.is_valid_string(text):
            return jsonify({"error": "Message text is required"}), 400
        if len(text) > 10000:
            return jsonify({"error": "Message text is too long"}), 400

        result = engine.analyze(text, channel)
        reports.add(result)
        return jsonify(result)

    @app.get("/api/reports")
    def report_list():
        return jsonify({"reports": reports.recent()})

    @app.get("/api/stats")
    def stats():
        return jsonify(reports.stats())

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=ConfigManager().get("debug", False))
