from src.core.validator import Validator
from .normalize import clean_text
from .scorer import score_message
from .adapters import registry
import re
from .brands import BRANDS
from .domain_checks import deep_scan_url


class ThreatEngine:
    def analyze(self, text: str, channel: str = "sms", sender: str = "", deep_scan: bool = False):
        raw = Validator.normalize_text(text)
        cleaned = clean_text(raw)
        result = score_message(channel, cleaned, sender)
        if deep_scan:
            deep_results = []
            for url_item in result.get("urls", []):
                deep = deep_scan_url(url_item["url"], lookalike=any(
                    finding["id"] in {"brand_in_domain", "lookalike_domain"}
                    for finding in url_item.get("findings", [])
                ))
                deep_results.append({"url": url_item["url"], **deep})
                fake_score = deep["fake_website"]["score"]
                if fake_score >= 30:
                    result["score"] = min(100, result["score"] + fake_score // 2)
                    result["signals"].append({
                        "id": "deep_fake_website",
                        "label": "Deep link reputation warning",
                        "category": "Other",
                        "weight": fake_score // 2,
                        "points": fake_score // 2,
                        "explanation": "Deep scan found young-domain, brand-lookalike or invalid-certificate indicators.",
                        "matches": [],
                    })
            result["deep_scan"] = deep_results
        result.pop("text_hash", None)
        return result

    def analyze_chat(self, text: str):
        extracted = registry.get("whatsapp").extract(text)
        if extracted.get("type") != "chat":
            result = self.analyze(extracted["text"], "whatsapp")
            return {"type": "chat", "chat": {"total": 1, "flagged": int(result["score"] >= 30),
                                              "scam": int(result["verdict"] == "Likely Scam"),
                                              "worst_id": "1"}, "messages": [{"id": "1", "sender": extracted["sender"],
                                                                              "timestamp": extracted["timestamp"],
                                                                              "result": result}]}
        results = []
        for message in extracted["messages"]:
            result = self.analyze(message["text"], "whatsapp")
            if message["meta"].get("forwarded"):
                result["score"] = min(100, result["score"] + 8)
                result["signals"].append({"id": "forwarded", "label": "Forwarded many times",
                                          "category": "Other", "weight": 8, "points": 8,
                                          "explanation": "The message was marked as widely forwarded.",
                                          "matches": []})
            results.append({"id": message["id"], "sender": message["sender"], "timestamp": message["timestamp"],
                            "result": result})
        worst = max(results, key=lambda item: item["result"]["score"]) if results else None
        flagged = sum(item["result"]["score"] >= 30 for item in results)
        scam = sum(item["result"]["verdict"] == "Likely Scam" for item in results)
        return {"type": "chat",
                "chat": {"total": len(results), "flagged": flagged, "scam": scam,
                         "worst_id": worst["id"] if worst else None},
                "messages": results}

    def analyze_email(self, text: str):
        extracted = registry.get("email").extract(text)
        result = self.analyze(extracted["text"], "email")
        meta = extracted["meta"]
        from_header = meta.get("from", "")
        reply_to = meta.get("reply_to", "")
        from_match = re.search(r"<([^>]+)>", from_header)
        from_address = from_match.group(1).lower() if from_match else from_header.lower()
        from_name = re.sub(r"<[^>]+>", "", from_header).lower()
        reply_match = re.search(r"<([^>]+)>", reply_to)
        reply_address = reply_match.group(1).lower() if reply_match else reply_to.lower()
        for brand, data in BRANDS.items():
            official = data["domains"]
            if any(token in from_name for token in data["tokens"]) and not any(address.endswith(domain) for address in [from_address] for domain in official):
                result["score"] = min(100, result["score"] + 40)
                result["signals"].append({"id": "display_name_spoof", "label": "Brand display-name spoof",
                                          "category": data["category"], "weight": 40, "points": 40,
                                          "explanation": f"The sender display name claims {brand} but the address is not official.",
                                          "matches": []})
        if reply_address:
            reply_domain = reply_address.rsplit("@", 1)[-1]
            sender_domain = from_address.rsplit("@", 1)[-1]
            if reply_domain and sender_domain and reply_domain != sender_domain:
                result["score"] = min(100, result["score"] + 20)
                result["signals"].append({"id": "reply_to_mismatch", "label": "Reply-To mismatch",
                                          "category": "Impersonation", "weight": 20, "points": 20,
                                          "explanation": "The Reply-To address is on a different domain from the sender.",
                                          "matches": []})
        for anchor in re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', text, re.I | re.S):
            href, label = anchor
            href_domain = re.findall(r"https?://([^/]+)", href, re.I)
            label_domain = re.findall(r"([a-z0-9-]+\.[a-z]{2,})", re.sub("<[^>]+>", "", label), re.I)
            if href_domain and label_domain and href_domain[0].lower().split(":")[0] != label_domain[0].lower():
                result["score"] = min(100, result["score"] + 45)
                result["signals"].append({"id": "anchor_mismatch", "label": "Anchor text domain mismatch",
                                          "category": "Impersonation", "weight": 45, "points": 45,
                                          "explanation": "Visible link text names a domain different from the actual href.",
                                          "matches": []})
        dangerous_attachments = {"exe", "apk", "scr", "zip", "html", "js", "bat", "jar", "vbs", "iso"}
        attachment_names = meta.get("attachments", [])
        for name in attachment_names:
            if str(name).rsplit(".", 1)[-1].lower() in dangerous_attachments:
                result["score"] = min(100, result["score"] + 35)
                result["signals"].append({"id": "dangerous_attachment", "label": "Dangerous attachment",
                                          "category": "Other", "weight": 35, "points": 35,
                                          "explanation": "The email contains an executable or archive attachment.",
                                          "matches": []})
        return result
