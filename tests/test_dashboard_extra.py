from app import create_app


def test_timeline_heatmap_reputation_and_breach_api(tmp_path):
    app = create_app({"TESTING": True, "DATABASE_PATH": tmp_path / "test.db"})
    client = app.test_client()
    assert client.get("/api/timeline").status_code == 200
    assert client.get("/api/heatmap").status_code == 200
    reputation = client.post("/api/reputation", json={"number": "0000000000", "domain": "example.xyz"})
    assert reputation.status_code == 200
    breach = client.post("/api/breach", json={"email": "", "password": "", "phone": "0000000000"})
    assert breach.status_code == 200
