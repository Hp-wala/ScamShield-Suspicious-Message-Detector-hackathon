import sqlite3

from app import create_app


def test_analyze_api_and_privacy(tmp_path):
    database = tmp_path / "test.db"
    app = create_app({"TESTING": True, "DATABASE_PATH": database})
    client = app.test_client()

    response = client.post("/api/analyze", json={
        "channel": "sms",
        "text": "KYC failed. Send OTP now: http://suspicious.example",
    })
    assert response.status_code == 200
    payload = response.get_json()
    assert "text_hash" not in payload
    assert set(payload) >= {"channel", "text", "score", "verdict", "category", "confidence", "signals", "urls", "advice"}

    with sqlite3.connect(database) as connection:
        row = connection.execute(
            "SELECT channel, category, risk_score, text_hash, created_at FROM reports"
        ).fetchone()
    assert row is not None


def test_invalid_channel(tmp_path):
    app = create_app({"TESTING": True, "DATABASE_PATH": tmp_path / "test.db"})
    response = app.test_client().post("/api/analyze", json={"channel": "voice", "text": "hello"})
    assert response.status_code == 400


def test_report_duplicate_feedback_stats_and_examples(tmp_path):
    app = create_app({"TESTING": True, "DATABASE_PATH": tmp_path / "test.db"})
    client = app.test_client()
    report = {
        "channel": "sms",
        "category": "Bank/KYC",
        "risk_score": 70,
        "message_hash": "a" * 64,
    }
    first = client.post("/api/report", json=report)
    second = client.post("/api/report", json=report)
    assert first.status_code == 201
    assert second.get_json()["status"] == "duplicate"

    feedback = client.post("/api/feedback", json={"channel": "sms", "verdict": "Likely Scam", "correct": True})
    assert feedback.status_code == 200

    stats = client.get("/api/stats")
    assert stats.status_code == 200
    assert stats.get_json()["total_reports"] == 1
    assert len(stats.get_json()["last_7_days"]) == 7

    examples = client.get("/api/examples")
    assert examples.status_code == 200
    assert len(examples.get_json()["examples"]) == 9


def test_whatsapp_chat_alias_and_bad_input(tmp_path):
    app = create_app({"TESTING": True, "DATABASE_PATH": tmp_path / "test.db"})
    client = app.test_client()
    chat = "12/03/24, 9:41 pm - Ravi: Aapka account blocked hai. Share OTP."
    response = client.post("/api/analyze-chat", json={"channel": "whatsapp", "text": chat})
    assert response.status_code == 200
    assert response.get_json()["type"] == "chat"
    assert client.post("/api/analyze", json={"channel": "sms", "text": ""}).status_code == 400
