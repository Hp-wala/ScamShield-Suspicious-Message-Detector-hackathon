"""Combine category rules and URL findings into an explainable verdict."""
from .advice import get_advice
from .normalize import message_hash
from .rules import RULES, NEGATIVE_RULES, find_rule_matches
from .urls import extract_urls, analyze_url
from .brands import BRANDS
from .ml_signal import ml_signal, MODEL

HOOKS = {"prize", "account_threat", "delivery", "utility", "digital_arrest", "job", "investment", "upi", "relative", "government"}
ASKS = {"credential_request", "advance_fee", "kyc_update", "call_number", "apk", "money_request", "move_to_chat"}


def score_message(channel: str, text: str, sender: str = "", use_ml: bool = True) -> dict:
    cleaned = text
    lowercase = cleaned.lower()
    url_items = extract_urls(cleaned)
    suspicious_url = any(analyze_url(item["url"])["score"] >= 20 for item in url_items)

    signals = []
    category_points = {}
    positive_ids = set()
    for rule in RULES:
        matches = find_rule_matches(cleaned, rule)
        if not matches:
            continue
        if rule.id == "credential_request":
            matches = [m for m in matches if not re_negated(lowercase, m["start"])]
        if not matches:
            continue
        extra = min(12, max(0, len(matches) - 1) * 4)
        points = rule.weight + extra
        signals.append({"id": rule.id, "label": rule.label, "category": rule.category, "weight": rule.weight,
                        "points": points, "explanation": rule.explanation, "matches": matches})
        positive_ids.add(rule.id)
        category_points[rule.category] = category_points.get(rule.category, 0) + points

    if len([ch for ch in cleaned if ch.isalpha() and ch.isupper()]) / max(1, len([ch for ch in cleaned if ch.isalpha()])) > .5 and len(cleaned) >= 20:
        signals.append({"id": "caps", "label": "Mostly uppercase", "category": "General", "weight": 5, "points": 5,
                        "explanation": "The message is unusually capitalized.", "matches": []})
    if cleaned.count("!") >= 3:
        signals.append({"id": "exclamation", "label": "Repeated exclamation marks", "category": "General", "weight": 4, "points": 4,
                        "explanation": "The message uses repeated exclamation marks.", "matches": []})

    if sender:
        digits = "".join(ch for ch in sender if ch.isdigit())
        if len(digits) == 10 and not re.search(r"\b[A-Z]{2,}-", sender):
            signals.append({"id": "personal_sender", "label": "Personal-number sender", "category": "Impersonation", "weight": 15, "points": 15,
                            "explanation": "A personal 10-digit number is used instead of an official sender ID.", "matches": []})

    if not suspicious_url:
        for rule in NEGATIVE_RULES:
            matches = find_rule_matches(cleaned, rule)
            if matches:
                points = rule.weight
                signals.append({"id": rule.id, "label": rule.label, "category": rule.category, "weight": rule.weight,
                                "points": points, "explanation": rule.explanation, "matches": matches})

    urls = []
    for item in url_items:
        details = analyze_url(item["url"])
        details["span"] = item["span"]
        urls.append(details)
        positive_ids.add("dangerous url")

    if positive_ids & HOOKS and positive_ids & ASKS:
        signals.append({"id": "combination", "label": "Hook plus action request", "category": "General", "weight": 15,
                        "points": 15, "explanation": "The message combines a threat or lure with an action request.", "matches": []})
    if "urgency" in positive_ids and (positive_ids & HOOKS or positive_ids & ASKS):
        signals.append({"id": "urgency_combo", "label": "Urgency plus action", "category": "General", "weight": 10,
                        "points": 10, "explanation": "Urgency is combined with a scam hook or request.", "matches": []})

    probability = MODEL.predict_proba(text) if use_ml else 0.5
    ml_result = ml_signal(text)
    rule_driven = bool(positive_ids & (HOOKS | ASKS)) or bool(urls)
    if use_ml and ml_result and rule_driven:
        signals.append({
            "id": ml_result["id"],
            "label": ml_result["label"],
            "category": ml_result["category"],
            "weight": ml_result["weight"],
            "points": ml_result["points"],
            "explanation": ml_result["explanation"],
            "matches": [],
        })

    positive = [s for s in signals if s["points"] > 0]
    score = 0
    category_totals = {}
    for signal in positive:
        category = signal["category"]
        existing = sum(1 for s in positive if s["category"] == category)
        category_order = sum(1 for s in positive[:positive.index(signal) + 1] if s["category"] == category)
        factor = 1.0 if category_order == 1 else .6 if category_order == 2 else .4 if category_order == 3 else .3
        points = round(signal["points"] * factor)
        score += points
        category_totals[category] = category_totals.get(category, 0) + points
    for url in urls:
        score += round(.7 * url["score"])
    score += sum(s["points"] for s in signals if s["points"] < 0)
    score = max(0, min(100, score))

    if score < 30:
        verdict = "Safe"
    elif score < 60:
        verdict = "Suspicious"
    else:
        verdict = "Likely Scam"

    category = max(category_totals, key=category_totals.get) if category_totals else "Other"
    confidence = "Low" if score < 30 or len(signals) < 2 else "Medium" if score < 75 else "High"
    return {
        "channel": channel,
        "text": cleaned,
        "score": score,
        "verdict": verdict,
        "category": category,
        "confidence": confidence,
        "signals": signals,
        "urls": urls,
        "advice": get_advice(category),
        "text_hash": message_hash(cleaned),
        "text_model_probability": round(probability, 4),
        "ml": {
            "available": MODEL.model is not None,
            "scam_probability": round(probability, 4),
        },
    }


def re_negated(text: str, start: int) -> bool:
    prefix = text[max(0, start - 60):start]
    return bool(__import__("re").search(r"\b(do not|never|don['’]t)\b", prefix, __import__("re").I))
