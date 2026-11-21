import json
from pathlib import Path

from src.threat.known_scams import known_scam_check
from src.threat.reputation import scammer_number_lookup, community_report_count
from src.report_store import ReportStore
from src.threat.scorer import score_message


def test_known_scam_database_size():
    path = Path(__file__).resolve().parents[1] / "data" / "known_scams.json"
    patterns = json.loads(path.read_text(encoding="utf-8"))
    assert len(patterns) >= 50


def test_known_scam_check_and_signal():
    known = known_scam_check(text="Pay fee for SBI account blocked KYC")
    assert known["matched"]
    result = score_message("sms", "Pay fee for SBI account blocked KYC")
    assert "known_scam" in {signal["id"] for signal in result["signals"]}


def test_number_hash_and_domain_reputation(tmp_path):
    store = ReportStore(tmp_path / "reports.db")
    lookup = scammer_number_lookup("0000000000", store)
    assert lookup["status"] == "available"
    assert len(lookup["number_hash"]) == 64
    domain = community_report_count("example.xyz", "domain", store)
    assert domain["community_report_count"] == 0
