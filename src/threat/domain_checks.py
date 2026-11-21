import ipaddress
import json
import os
import socket
import ssl
from datetime import datetime, timezone
from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import URLError, HTTPError


def is_public_host(host):
    if not host:
        return False
    try:
        ipaddress.ip_address(host)
        return not ipaddress.ip_address(host).is_private and not ipaddress.ip_address(host).is_loopback
    except ValueError:
        try:
            for address in {item[4][0] for item in socket.getaddrinfo(host, None)}:
                ip = ipaddress.ip_address(address)
                if ip.is_private or ip.is_loopback or ip.is_link_local:
                    return False
            return True
        except socket.gaierror:
            return False


def redirect_chain(url):
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not is_public_host(parsed.hostname):
        return {"status": "skipped", "reason": "private_or_invalid_host", "chain": []}

    class NoDownloadRedirect(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return Request(newurl, method="HEAD", headers=req.headers)

    chain = [url]
    opener = build_opener(NoDownloadRedirect)
    try:
        response = opener.open(Request(url, method="HEAD"), timeout=5)
        final_url = response.geturl()
        if final_url not in chain:
            chain.append(final_url)
        status = "ok"
    except (URLError, HTTPError, TimeoutError, OSError):
        status = "network_error"
    return {"status": status, "chain": chain[:6], "hops": max(0, len(chain) - 1)}


def whois_domain(domain):
    if not domain or not is_public_host(domain):
        return {"status": "skipped", "reason": "private_or_invalid_host"}
    try:
        import whois
    except ImportError:
        return {"status": "skipped", "reason": "python-whois_not_installed"}
    try:
        record = whois.whois(domain)
        created = record.creation_date
        if isinstance(created, list):
            created = created[0]
        if created:
            if created.tzinfo:
                created = created.astimezone(timezone.utc).replace(tzinfo=None)
            age_days = (datetime.now(timezone.utc).replace(tzinfo=None) - created).days
        else:
            age_days = None
        return {"status": "ok", "creation_date": created.isoformat() if created else None, "age_days": age_days}
    except Exception:
        return {"status": "network_error"}


def ssl_certificate(domain):
    if not domain or not is_public_host(domain):
        return {"status": "skipped", "reason": "private_or_invalid_host"}
    context = ssl.create_default_context()
    try:
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as tls:
                cert = tls.getpeercert()
                not_after = ssl.cert_time_to_seconds(cert["notAfter"])
                expiry = datetime.fromtimestamp(not_after, timezone.utc).isoformat()
                return {
                    "status": "ok",
                    "issuer": dict(x[0] for x in cert.get("issuer", [])),
                    "expiry": expiry,
                    "hostname_valid": True,
                }
    except ssl.SSLCertVerificationError as exc:
        return {"status": "invalid", "reason": "certificate_validation_failed", "detail": str(exc)[:200]}
    except (socket.timeout, ConnectionError, OSError):
        return {"status": "network_error"}


def safe_browsing_check(url):
    key = os.getenv("SAFE_BROWSING_API_KEY")
    if not key:
        return {"status": "skipped", "reason": "missing_api_key"}
    host = urlparse(url).hostname
    if not host or not is_public_host(host):
        return {"status": "skipped", "reason": "private_or_invalid_host"}
    import urllib.request
    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={key}"
    payload = json.dumps({
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}],
        }
    }).encode("utf-8")
    request = urllib.request.Request(endpoint, data=payload, method="POST", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            return {"status": "ok", "threat_matches": data.get("matches", [])}
    except (URLError, HTTPError, TimeoutError, OSError):
        return {"status": "network_error"}


def virustotal_url_check(url):
    key = os.getenv("VT_API_KEY")
    if not key:
        return {"status": "skipped", "reason": "missing_api_key"}
    host = urlparse(url).hostname
    if not host or not is_public_host(host):
        return {"status": "skipped", "reason": "private_or_invalid_host"}
    import hashlib
    from urllib.parse import urlencode
    import urllib.request
    try:
        import base64
        identifier = base64.urlsafe_b64encode(url.encode("utf-8")).decode("ascii").rstrip("=")
        request = urllib.request.Request(
            f"https://www.virustotal.com/api/v3/urls/{identifier}",
            headers={"x-apikey": key},
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            return {"status": "ok", "stats": stats}
    except (URLError, HTTPError, TimeoutError, OSError):
        return {"status": "network_error"}


def fake_website_detector(domain, age_days=None, lookalike=False, ssl_status=None):
    score = 0
    if age_days is not None and age_days < 30:
        score += 30
    if lookalike:
        score += 40
    if ssl_status in {"invalid", "network_error"}:
        score += 30
    return {"score": min(100, score), "young_domain": age_days is not None and age_days < 30,
            "brand_lookalike": lookalike, "ssl_status": ssl_status}


def deep_scan_url(url, lookalike=False):
    parsed = urlparse(url)
    domain = parsed.hostname or ""
    redirect = redirect_chain(url)
    age = whois_domain(domain)
    ssl_result = ssl_certificate(domain)
    fake = fake_website_detector(domain, age.get("age_days"), lookalike, ssl_result.get("status"))
    return {
        "redirect": redirect,
        "whois": age,
        "ssl": ssl_result,
        "safe_browsing": safe_browsing_check(url),
        "virustotal": virustotal_url_check(url),
        "fake_website": fake,
    }
