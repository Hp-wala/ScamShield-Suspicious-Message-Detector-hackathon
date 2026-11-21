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
    assert "text" not in payload
    assert len(payload["text_hash"]) == 64

    with sqlite3.connect(database) as connection:
        row = connection.execute(
            "SELECT channel, category, risk_score, text_hash, timestamp FROM reports"
        ).fetchone()
    assert row is not None
    assert "KYC" not in repr(row)


def test_invalid_channel(tmp_path):
    app = create_app({"TESTING": True, "DATABASE_PATH": tmp_path / "test.db"})
    response = app.test_client().post("/api/analyze", json={"channel": "voice", "text": "hello"})
    assert response.status_code == 400
