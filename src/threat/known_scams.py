import hashlib
import json
import re
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "known_scams.json"


def hash_number(number):
    value = re_digits(number)
    return hashlib.sha256(value.encode("utf-8")).hexdigest() if value else ""


def re_digits(value):
    return "".join(ch for ch in str(value or "") if ch.isdigit())


def load_patterns():
    try:
        return json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []


def known_scam_check(text="", number="", domain=""):
    text_lower = str(text or "").lower()
    domain_lower = str(domain or "").lower().strip(".")
    number_hash = hash_number(number)
    matches = []
    for item in load_patterns():
        phrase_tokens = [token for token in re.findall(r"[a-z0-9]+", item["phrase"].lower()) if len(token) > 2]
        text_tokens = set(re.findall(r"[a-z0-9]+", text_lower))
        overlap = len(set(phrase_tokens) & text_tokens)
        anchor = len(set(phrase_tokens) & text_tokens) >= 3
        if anchor:
            matches.append(item)
            continue
        if domain_lower and domain_lower in [d.lower() for d in item.get("domains", [])]:
            matches.append(item)
            continue
        if number and re_digits(number) in item.get("numbers", []):
            matches.append(item)
    return {
        "matched": bool(matches),
        "count": len(matches),
        "categories": sorted({item["category"] for item in matches}),
        "number_hash": number_hash,
    }
