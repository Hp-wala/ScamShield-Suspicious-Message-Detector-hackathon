from .known_scams import hash_number


def scammer_number_lookup(number, report_store=None):
    number_hash = hash_number(number)
    if not number_hash:
        return {"status": "skipped", "reason": "missing_number", "reputation_score": 0}
    count = 0
    if report_store:
        count = report_store.reputation("number", number_hash)["count"]
    reputation_score = min(100, count * 20)
    return {
        "status": "available",
        "number_hash": number_hash,
        "community_report_count": count,
        "reputation_score": reputation_score,
    }


def community_report_count(indicator, kind="domain", report_store=None):
    import hashlib
    normalized = str(indicator or "").strip().lower()
    indicator_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest() if normalized else ""
    count = report_store.reputation(kind, indicator_hash)["count"] if report_store and indicator_hash else 0
    return {"kind": kind, "indicator_hash": indicator_hash, "community_report_count": count}
