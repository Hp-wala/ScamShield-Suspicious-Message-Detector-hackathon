import ipaddress
import re
from urllib.parse import urlparse

from .brands import BRANDS

SHORTENERS = {"bit.ly", "tinyurl.com", "cutt.ly", "t.co", "rb.gy", "is.gd", "shorturl.at"}
RISKY_TLD = {".xyz", ".top", ".click", ".live", ".icu", ".buzz", ".cfd", ".sbs", ".vip", ".rest", ".gq", ".tk", ".ml", ".cf", ".work", ".support"}
PATH_WORDS = {"login", "verify", "update", "kyc", "secure", "claim", "refund", "otp", "bonus", "reward", "account", "suspend", "unlock", "confirm"}
TLD_PATTERN = r"(com|in|org|net|gov\.in|nic\.in|co\.in|bank\.in|sbi|edu|app)"
URL_PATTERN = re.compile(
    r"(?<![\w@])(?:(?:hxxps?|https?):\/\/|www\.)?"
    r"[a-z0-9-]+(?:\[\.\]|\(\.\)|\.|\s+dot\s+)[a-z0-9.-]*"
    r"[a-z0-9-]+\.[a-z]{2,}(?:/[^\s]*)?",
    re.I,
)


def _levenshtein(a: str, b: str) -> int:
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (ca != cb)))
        previous = current
    return previous[-1]


def extract_urls(text: str) -> list[dict]:
    results = []
    hxxp_pattern = re.compile(r"(?<![\w@])hxxps?://[^\s]+", re.I)
    for match in hxxp_pattern.finditer(text):
        url = match.group(0).strip(".,);]")
        results.append({"url": url, "span": [match.start(), match.end()]})
    matches = list(URL_PATTERN.finditer(text))
    for match in matches:
        url = match.group(0).strip(".,);]")
        if "@" in url:
            continue
        results.append({"url": url, "span": [match.start(), match.end()]})
    bare_pattern = re.compile(r"(?<![@\w])(?:www\.)?[a-z0-9-]+\.[a-z]{2,}(?:/[^\s]*)?", re.I)
    for match in bare_pattern.finditer(text):
        span = [match.start(), match.end()]
        if any(span[0] >= existing["span"][0] and span[1] <= existing["span"][1] for existing in results):
            continue
        url = match.group(0).strip(".,);]")
        if "@" not in url:
            results.append({"url": url, "span": span})
    return results


def registered_domain(host: str) -> str:
    labels = host.rstrip(".").split(".")
    if len(labels) >= 3 and ".".join(labels[-2:]) in {"co.in", "gov.in", "bank.in", "nic.in"}:
        return ".".join(labels[-3:])
    if len(labels) >= 2:
        return ".".join(labels[-2:])
    return host


def analyze_url(url: str) -> dict:
    obfuscated = url
    obfuscated = re.sub(r"^hxxp", "http", obfuscated, flags=re.I)
    obfuscated = obfuscated.replace("[.]", ".").replace("(.)", ".").replace(" dot ", ".")
    parsed = urlparse(obfuscated if "://" in obfuscated else "http://" + obfuscated)
    host = (parsed.hostname or "").lower()
    host = host[4:] if host.startswith("www.") else host
    registered = registered_domain(host)
    score = 0
    findings = []

    def add(id_, label, weight, explanation):
        nonlocal score
        score += weight
        findings.append({"id": id_, "label": label, "weight": weight, "explanation": explanation})

    if registered in SHORTENERS:
        add("shortener", "Shortened link", 30, "This URL uses a known link shortener.")
    try:
        ipaddress.ip_address(host)
        add("ip_host", "IP-address host", 35, "The link uses an IP address instead of a domain.")
    except ValueError:
        pass
    if "@" in url:
        add("at_symbol", "Deceptive @ symbol", 30, "The link contains an @ symbol that can hide its real destination.")
    if "xn--" in host:
        add("punycode", "Punycode domain", 35, "The domain uses punycode and may imitate another website.")
    if len([part for part in host.split(".") if part]) >= 4:
        add("many_subdomains", "Many subdomains", 20, "The link uses an unusually complex subdomain chain.")
    if host.count("-") >= 2:
        add("hyphens", "Many hyphens", 15, "The domain contains several hyphens.")
    if any(host.endswith(tld) for tld in RISKY_TLD):
        add("risky_tld", "Risky domain extension", 25, "The domain uses an extension often associated with scams.")
    if not obfuscated.lower().startswith("https://"):
        add("no_https", "No HTTPS", 12, "The link does not use HTTPS.")
    if len(url) > 100:
        add("long_url", "Very long URL", 10, "The URL is unusually long.")
    path = (parsed.path or "").lower()
    if any(word in path for word in PATH_WORDS):
        add("path_words", "Sensitive path words", 12, "The path contains account, verification or reward words.")

    official = {domain for data in BRANDS.values() for domain in data["domains"]}
    official_match = host in official or registered in official or host.endswith(".gov.in") or host.endswith(".nic.in") or host == "wa.me"
    if not official_match:
        normalized_host = host.replace("0", "o").replace("1", "l").replace("rn", "m").replace("vv", "w")
        for domain in official:
            if _levenshtein(normalized_host, domain) <= 2:
                add("lookalike_domain", "Lookalike domain", 50, "The domain closely resembles an official brand domain.")
                break
        for brand, data in BRANDS.items():
            for token in data["tokens"]:
                if token.lower().replace(" ", "") in normalized_host.replace("-", "").replace(".", ""):
                    add("brand_in_domain", "Brand name in unfamiliar domain", 55, f"The URL claims a {brand}-like brand but is not on an official domain.")
                    break
    verdict = "safe" if score < 20 else "suspicious" if score < 50 else "dangerous"
    return {"url": url, "verdict": verdict, "score": min(100, score), "findings": findings}
