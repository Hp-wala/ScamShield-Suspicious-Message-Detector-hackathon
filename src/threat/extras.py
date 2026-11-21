import re
import unicodedata

SHORTFORMS = {
    "u": "you", "ur": "your", "pls": "please", "plz": "please",
    "acc": "account", "a/c": "account", "txn": "transaction",
    "amt": "amount", "bal": "balance", "kyc": "kyc", "asap": "as soon as possible",
}
STOPWORDS = {"a", "an", "the", "is", "are", "was", "were", "to", "of", "and", "or", "for", "in", "on", "with"}


def remove_emoji(text):
    return "".join(ch for ch in str(text or "") if unicodedata.category(ch)[0] != "S")


def expand_shortforms(text):
    result = str(text or "")
    for short, full in SHORTFORMS.items():
        result = re.sub(r"(?<!\w)" + re.escape(short).replace(r"\/", r"\/") + r"(?!\w)", full, result, flags=re.I)
    return result


def remove_repeated_chars(text):
    return re.sub(r"(.)\1{2,}", r"\1", str(text or ""), flags=re.I)


def detect_language(text):
    text = str(text or "")
    devanagari = sum("\u0900" <= ch <= "\u097f" for ch in text)
    latin = sum(ch.isascii() and ch.isalpha() for ch in text)
    roman_hindi = bool(re.search(r"\b(?:namaste|aap|aapka|aapke|ka|ki|ke|karo|hai|hain|mat|bhejo|jaldi|turant)\b", text, re.I))
    if devanagari and latin:
        return "hinglish"
    if devanagari:
        return "hindi"
    if roman_hindi:
        return "hinglish"
    return "english"


def extract_money(text):
    pattern = re.compile(r"(?:(?:rs\.?|inr|rupees?|₹)\s*[\d,]+(?:\.\d+)?|\$\s*[\d,]+(?:\.\d+)?|[\d,]+\s*(?:/-|rupees?))", re.I)
    return pattern.findall(str(text or ""))


def extract_emails(text):
    return re.findall(r"(?<![\w.-])[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9-]+(?:\.[a-z0-9-]+)+(?![\w.-])", str(text or ""), re.I)


def detect_obfuscation(text):
    text = str(text or "").lower()
    patterns = (
        r"\b[bv]@nk\b", r"\b0tp\b", r"\bcl[1i]ck\b", r"\bv3rify\b",
        r"\bk[y1][cç]\b", r"\bp[1i]n\b", r"\ba[cç][c]?ount\b",
    )
    hits = [pattern for pattern in patterns if re.search(pattern, text, re.I)]
    return {"detected": bool(hits), "patterns": hits}


def detect_mixed_script(text):
    text = str(text or "")
    latin = bool(re.search(r"[A-Za-z]", text))
    greek = bool(re.search(r"[Α-Ωα-ω]", text))
    cyrillic = bool(re.search(r"[А-Яа-я]", text))
    devanagari = bool(re.search(r"[अ-ह]", text))
    homoglyph = greek or cyrillic
    return {
        "mixed_script": latin and (devanagari or homoglyph),
        "homoglyph": homoglyph,
        "latin": latin,
        "devanagari": devanagari,
    }


def message_length(text):
    return len(str(text or ""))


def digit_ratio(text):
    text = str(text or "")
    if not text:
        return 0.0
    digits = sum(ch.isdigit() for ch in text)
    return digits / len(text)


def spelling_grammar_anomaly(text):
    text = str(text or "")
    score = 0
    if re.search(r"[a-z]{1}[A-Z][a-z]", text):
        score += 2
    if len(re.findall(r"[^\w\s]", text)) >= 8:
        score += 2
    if re.search(r"\b[bcdfghjklmnpqrstvwxyz]{6,}\b", text.lower()):
        score += 2
    if len(text.split()) >= 8 and not re.search(r"[.!?]", text):
        score += 1
    return min(score, 10)


def optional_stopwords(text):
    words = re.findall(r"[a-z0-9]+", str(text or "").lower())
    return [word for word in words if word not in STOPWORDS]


def optional_stem(text):
    words = optional_stopwords(text)
    result = []
    for word in words:
        if len(word) > 5 and word.endswith("ing"):
            word = word[:-3]
        elif len(word) > 4 and word.endswith("ed"):
            word = word[:-2]
        elif len(word) > 4 and word.endswith("s"):
            word = word[:-1]
        result.append(word)
    return result
