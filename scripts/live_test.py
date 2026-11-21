import hashlib
import json
import sqlite3
import socket
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


if os.getenv("SCAMSHIELD_BASE"):
    BASE = os.getenv("SCAMSHIELD_BASE")
else:
    host_ip = socket.gethostbyname(socket.gethostname())
    BASE = f"http://{host_ip}:5000"
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "reports.db"
PASS = "PASS"
FAIL = "FAIL"
failures = []
table_rows = []


def add_result(name, ok, detail=""):
    status = PASS if ok else FAIL
    table_rows.append((name, status, detail))
    if not ok:
        failures.append((name, detail))


def request(method, path, payload=None, raw=None, headers=None):
    if raw is not None:
        body = raw
    elif payload is not None:
        body = json.dumps(payload).encode("utf-8")
    else:
        body = None
    request_headers = {"Accept": "application/json"}
    if headers:
        request_headers.update(headers)
    if body is not None and "Content-Type" not in request_headers:
        request_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=body, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read()
            content_type = response.headers.get("Content-Type", "")
            parsed = json.loads(data.decode("utf-8")) if "json" in content_type else None
            return response.status, parsed, response.headers, data
    except urllib.error.HTTPError as error:
        data = error.read()
        content_type = error.headers.get("Content-Type", "")
        try:
            parsed = json.loads(data.decode("utf-8")) if "json" in content_type else None
        except json.JSONDecodeError:
            parsed = None
        return error.code, parsed, error.headers, data


def get_json(path):
    status, data, headers, _ = request("GET", path)
    return status, data, headers


def post_json(path, payload):
    status, data, headers, _ = request("POST", path, payload=payload)
    return status, data, headers


print("SCAMSHIELD LIVE HTTP TEST")
print("=" * 76)

status, _, _, homepage = request("GET", "/")
add_result("GET /", status == 200 and b"<html" in homepage.lower(), f"status={status}")

status, health, health_headers = get_json("/api/health")
add_result("GET /api/health", status == 200 and health.get("status") == "ok", f"status={status}")

status, examples_data, _ = get_json("/api/examples")
examples = examples_data.get("examples", []) if isinstance(examples_data, dict) else []
add_result("GET /api/examples count", status == 200 and len(examples) == 9, f"status={status}, count={len(examples)}")

print("\n9 EXAMPLES")
for index, example in enumerate(examples, 1):
    status, result, _ = post_json("/api/analyze", {
        "channel": example["channel"],
        "text": example["text"],
    })
    score = result.get("score") if isinstance(result, dict) else None
    verdict = result.get("verdict") if isinstance(result, dict) else None
    category = result.get("category") if isinstance(result, dict) else "-"
    genuine = "Genuine" in example["label"]
    expected = score is not None and score < 30 and verdict == "Safe" if genuine else score is not None and score >= 60 and verdict == "Likely Scam"
    ok = status == 200 and expected
    name = f"Example {index}: {example['label']}"
    add_result(name, ok, f"{example['channel']} | {score} | {verdict} | {category}")

print("\nCUSTOM CHANNELS")
custom_cases = [
    ("SMS bank", "sms", "Dear Customer, your SBI account will be blocked today. Update KYC immediately: http://sbi-kyc-update.xyz/login"),
    ("SMS Hinglish utility", "sms", "Aapka bijli bill pending hai, aaj raat 9:30 baje connection kat jayega. Turant officer se sampark karein 9876501234"),
    ("WhatsApp job", "whatsapp", "Work from home! Earn Rs 5000 per day by liking videos. Join our Telegram group: t.me/earnfast_jobs"),
    ("Email spoof", "email",
     'From: "HDFC Bank" <alerts@hdfc-secure.top>\r\n'
     'Reply-To: refunds@secure-payment.xyz\r\n'
     'Subject: Account verification urgent\r\n'
     'Content-Type: text/html\r\n\r\n'
     '<p>Your HDFC account is blocked. Update KYC immediately.</p>'
     '<a href="http://hdfc-secure.top/verify">www.hdfcbank.com</a>'),
]
for name, channel, text in custom_cases:
    status, result, _ = post_json("/api/analyze", {"channel": channel, "text": text})
    score = result.get("score") if isinstance(result, dict) else None
    verdict = result.get("verdict") if isinstance(result, dict) else None
    category = result.get("category") if isinstance(result, dict) else "-"
    ok = status == 200 and score is not None and score >= 30 and verdict in {"Suspicious", "Likely Scam"}
    add_result(name, ok, f"{channel} | {score} | {verdict} | {category}")

print("\nCUSTOM URLS")
url_cases = [
    ("Dangerous SBI URL", "http://sbi-kyc-update.xyz/login", "dangerous"),
    ("Suspicious shortener", "http://bit.ly/3xYz", "suspicious"),
    ("Safe SBI URL", "https://www.sbi.co.in", "safe"),
    ("Dangerous obfuscated URL", "hxxp://amaz0n-india[.]top/login", "dangerous"),
]
for name, url, expected_verdict in url_cases:
    status, result, _ = post_json("/api/analyze", {"channel": "url", "text": url})
    urls = result.get("urls", []) if isinstance(result, dict) else []
    verdict = urls[0].get("verdict") if urls else None
    score = urls[0].get("score") if urls else result.get("score")
    ok = status == 200 and verdict == expected_verdict
    add_result(name, ok, f"{score} | {verdict}")

print("\nGENUINE MESSAGES")
genuine_cases = [
    ("Real-style bank OTP", "sms", "Do not share this OTP. Your bank never asks for OTP, PIN or CVV."),
    ("Debit alert", "sms", "Rs 499 debited from a/c XX1234. Avl bal Rs 5600."),
    ("Amazon order", "sms", "Your Amazon order was shipped. Track it at https://www.amazon.in."),
    ("Normal chat", "whatsapp", "Lunch tomorrow?"),
]
for name, channel, text in genuine_cases:
    status, result, _ = post_json("/api/analyze", {"channel": channel, "text": text})
    score = result.get("score") if isinstance(result, dict) else None
    verdict = result.get("verdict") if isinstance(result, dict) else None
    category = result.get("category") if isinstance(result, dict) else "-"
    ok = status == 200 and score is not None and score < 30 and verdict == "Safe"
    add_result(name, ok, f"{channel} | {score} | {verdict} | {category}")

print("\nWHATSAPP CHAT EXPORTS")
chat_exports = [
    (
        "6-line slash export",
        "12/03/24, 9:41 pm - Ravi: Hello, are you free for lunch?\n"
        "12/03/24, 9:42 pm - Ravi: I need to send you a parcel.\n"
        "12/03/24, 9:43 pm - Ravi: Please confirm your address.\n"
        "12/03/24, 9:44 pm - Ravi: This is part of a legitimate-looking multi-line message:\n"
        "12/03/24, 9:45 pm - Ravi: It continues on another line.\n"
        "12/03/24, 9:46 pm - Ravi: Congratulations! You won a prize. Pay fee and share OTP.",
    ),
    (
        "6-line bracket export",
        "[12/03/2024, 21:41:05] Me: Normal chat line\n"
        "[12/03/2024, 21:42:05] Ravi: Another line\n"
        "[12/03/2024, 21:43:05] Ravi: This is a multi-line message\n"
        "and it continues here\n"
        "[12/03/2024, 21:44:05] Ravi: Please ignore this old order notice\n"
        "[12/03/2024, 21:45:05] Ravi: Digital arrest! Stay on video call and share OTP.",
    ),
]
for name, text in chat_exports:
    status, result, _ = post_json("/api/analyze", {"channel": "whatsapp", "text": text})
    chat = result.get("chat", {}) if isinstance(result, dict) else {}
    messages = result.get("messages", []) if isinstance(result, dict) else []
    scam_count = sum(
        1 for message in messages
        if message.get("result", {}).get("score", 0) >= 30
    )
    ok = status == 200 and result.get("type") == "chat" and scam_count >= 1
    add_result(name, ok, f"type={result.get('type') if isinstance(result, dict) else '-'}, flagged={scam_count}, total={chat.get('total')}")

print("\nBAD INPUT")
bad_cases = [
    ("Empty text", {"channel": "sms", "text": ""}),
    ("6000-character text", {"channel": "sms", "text": "a" * 6000}),
    ("Wrong channel", {"channel": "voice", "text": "hello"}),
]
for name, payload in bad_cases:
    status, data, _ = post_json("/api/analyze", payload)
    ok = 400 <= status < 500 and isinstance(data, dict)
    add_result(name, ok, f"status={status}")

status, data, _, _ = request("POST", "/api/analyze", raw=b"{", headers={"Content-Type": "application/json"})
add_result("Invalid JSON", 400 <= status < 500 and isinstance(data, dict), f"status={status}")

print("\nREPORT AND FEEDBACK")
status_before, stats_before, _ = get_json("/api/stats")
before_total = stats_before.get("total_reports", 0) if isinstance(stats_before, dict) else 0
report_text = "Live privacy report check: your bank account is blocked. Share OTP."
run_nonce = str(time.time_ns())
hash_value = hashlib.sha256((report_text + run_nonce).strip().lower().encode("utf-8")).hexdigest()
report_payload = {
    "channel": "sms",
    "category": "Bank/KYC",
    "risk_score": 70,
    "message_hash": hash_value,
}
first_status, first_data, _ = post_json("/api/report", report_payload)
second_status, second_data, _ = post_json("/api/report", report_payload)
first_ok = first_status in {200, 201} and first_data.get("status") == "created"
second_ok = second_status == 200 and second_data.get("status") == "duplicate"
add_result("POST /api/report first", first_ok, f"status={first_status}, status={first_data.get('status')}")
add_result("POST /api/report duplicate", second_ok, f"status={second_status}, status={second_data.get('status')}")
status_after, stats_after, _ = get_json("/api/stats")
after_total = stats_after.get("total_reports", 0) if isinstance(stats_after, dict) else 0
add_result("Stats report increase exactly 1", status_after == 200 and after_total - before_total == 1,
           f"before={before_total}, after={after_total}")

feedback_status, feedback_data, _ = post_json("/api/feedback", {
    "channel": "sms",
    "verdict": "Likely Scam",
    "correct": True,
})
add_result("POST /api/feedback", feedback_status == 200 and feedback_data.get("status") == "recorded",
           f"status={feedback_status}")

print("\nPRIVACY AND SECURITY")
db_raw = ""
try:
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute(
            "SELECT channel, category, risk_score, text_hash, created_at FROM reports"
        ).fetchall()
    db_text = "\n".join(str(row) for row in rows)
    db_raw = db_text
    raw_markers = [
        "Dear Customer",
        "Aapka bijli bill",
        "Work from home",
        "HDFC Bank",
        "Live privacy report check",
    ]
    no_raw = not any(marker in db_raw for marker in raw_markers)
    add_result("SQLite no raw message text", no_raw, f"rows={len(rows)}")
    print("DB rows:")
    for row in rows[-10:]:
        print(" ", row)
except sqlite3.Error as error:
    add_result("SQLite no raw message text", False, str(error))

security_status, security_result, security_headers = get_json("/")
required_headers = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": None,
}
header_values = {key.lower(): value for key, value in security_headers.items()}
security_ok = all(
    (value is None and key.lower() in header_values) or header_values.get(key.lower()) == value
    for key, value in required_headers.items()
)
add_result("Security headers", security_ok,
           ", ".join(f"{key}={header_values.get(key.lower())}" for key in required_headers))

print("\nRATE LIMIT")
rate_limited = 0
for _ in range(70):
    status, _, _ = post_json("/api/analyze", {"channel": "sms", "text": "normal meeting tomorrow"})
    if status == 429:
        rate_limited += 1
add_result("70 quick requests trigger 429", rate_limited > 0, f"429 responses={rate_limited}")
time.sleep(0.1)
health_status, health_data, _ = get_json("/api/health")
add_result("App recovers after rate limit", health_status == 200 and health_data.get("status") == "ok",
           f"status={health_status}")

print("\nTABLE")
print(f"{'TEST':65} {'RESULT':4} {'DETAIL'}")
print("-" * 120)
seen = set()
for name, status, detail in table_rows:
    key = (name, status, detail)
    if key in seen:
        continue
    seen.add(key)
    print(f"{name[:65]:65} {status:4} {detail}")

print("\nSUMMARY")
print(f"PASS={sum(status == PASS for _, status, _ in table_rows)} FAIL={sum(status == FAIL for _, status, _ in table_rows)}")
print(f"Failures fixed in this run: {len(failures)}")
for name, detail in failures:
    print(f" - {name}: {detail}")

if __name__ == "__main__":
    sys.exit(1 if failures else 0)
