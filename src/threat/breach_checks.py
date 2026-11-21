import hashlib
import json
import os
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def email_breach_check(email):
    key = os.getenv("HIBP_API_KEY")
    if not key:
        return {"status": "skipped", "reason": "missing_api_key", "breach_names": []}
    if not email or "@" not in email:
        return {"status": "skipped", "reason": "invalid_email", "breach_names": []}
    request = Request(
        f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
        headers={"hibp-api-key": key, "user-agent": "ScamShield"},
    )
    try:
        with urlopen(request, timeout=5) as response:
            breaches = json.loads(response.read().decode("utf-8"))
            names = sorted({item.get("Name") for item in breaches if item.get("Name")})
            return {"status": "ok", "breach_names": names}
    except HTTPError as exc:
        if exc.code == 404:
            return {"status": "ok", "breach_names": []}
        return {"status": "network_error", "breach_names": []}
    except (URLError, TimeoutError, OSError):
        return {"status": "network_error", "breach_names": []}


def password_breach_check(password):
    if not isinstance(password, str) or not password:
        return {"status": "skipped", "reason": "missing_password", "pwned": False}
    digest = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = digest[:5], digest[5:]
    try:
        with urlopen(f"https://api.pwnedpasswords.com/range/{prefix}", timeout=5) as response:
            lines = response.read().decode("ascii").splitlines()
        pwned = any(line.split(":")[0].upper() == suffix for line in lines)
        return {"status": "ok", "pwned": pwned}
    except (URLError, HTTPError, TimeoutError, OSError):
        return {"status": "network_error", "pwned": False}


def phone_breach_check(_phone):
    return {"status": "not_supported", "reason": "no_legal_phone_breach_api_configured"}
