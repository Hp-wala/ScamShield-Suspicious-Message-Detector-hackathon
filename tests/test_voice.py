from src.threat.voice import analyze_transcript
from src.threat.engine import ThreatEngine


def test_voice_transcript_analysis():
    result = analyze_transcript("You are under digital arrest. Stay on video call.", ThreatEngine())
    assert result["status"] == "ok"
    assert "text" not in result["analysis"]


def test_voice_empty_transcript():
    result = analyze_transcript("", ThreatEngine())
    assert result["status"] == "error"
