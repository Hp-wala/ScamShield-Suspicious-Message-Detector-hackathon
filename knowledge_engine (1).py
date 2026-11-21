# ==========================================================
# JARVIS AI
# KNOWLEDGE ENGINE
# Python 3.12
# ==========================================================
#
# This is the brain behind Training Mode. It does NOT use any
# LLM / Ollama. Everything here is rule-based: keyword + tag
# matching, synonym expansion, regex-based code analysis, and
# template-based project assembly.
#
# WHAT IT STORES (memory_data/ folder, same place memory.py
# already uses):
#
#   categories.json        -> the category / subcategory tree
#   knowledge_base.json     -> every fact / concept / code entry
#                               you teach, structured
#   snippet_library.json    -> code snippets extracted from
#                               taught code, grouped by "role"
#                               (login, database, file_handling..)
#   dependency_graph.json   -> which concepts relate to which
#                               (e.g. flask -> routing, sessions)
#
# HONEST LIMITATION (read this before expecting magic):
# There is no real "understanding" here. Matching is keyword +
# synonym based, and the "composer" only recombines code you
# have already taught it. It cannot invent a truly novel
# algorithm it has never seen. The more you teach it, the
# better it gets — it does not get smarter on its own.
# ==========================================================

import json
import os
import re
import datetime


# ==========================================================
# STORAGE LOCATIONS
# ==========================================================

DATA_DIR = "memory_data"
CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.json")
KNOWLEDGE_FILE = os.path.join(DATA_DIR, "knowledge_base.json")
SNIPPET_FILE = os.path.join(DATA_DIR, "snippet_library.json")
GRAPH_FILE = os.path.join(DATA_DIR, "dependency_graph.json")


# ==========================================================
# PRESET CATEGORY TREE (expandable — custom entries get
# merged in permanently and saved to disk)
# ==========================================================

DEFAULT_CATEGORIES = {
    "programming & technology": [
        "html", "css", "javascript", "typescript", "python", "java", "c",
        "c++", "c#", "php", "sql", "mongodb", "flask", "django", "fastapi",
        "react", "node.js", "apis", "git", "github", "linux", "networking",
        "cyber security", "machine learning", "artificial intelligence",
        "data structures", "algorithms", "web development",
        "mobile development", "other",
    ],
    "languages": [
        "english", "hindi", "assamese", "bengali", "french", "german",
        "japanese", "chinese", "grammar", "vocabulary", "other",
    ],
    "history": [
        "ancient", "medieval", "modern", "indian", "world",
        "freedom movement", "wars", "civilizations", "other",
    ],
    "science": ["other"],
    "mathematics": ["other"],
    "geography": ["other"],
    "business": ["other"],
    "law": ["other"],
    "medicine": ["other"],
    "literature": ["other"],
    "personal knowledge": ["other"],
}


# ==========================================================
# STOPWORDS (ignored when extracting tags from a sentence)
# ==========================================================

STOPWORDS = {
    "a", "an", "the", "is", "was", "were", "are", "am", "be", "been",
    "to", "of", "in", "on", "for", "and", "or", "it", "this", "that",
    "i", "you", "your", "my", "me", "do", "does", "did", "what", "who",
    "how", "why", "when", "where", "tell", "about", "please", "can",
    "could", "would", "should", "will", "with", "as", "at", "by",
    "so", "if", "not", "has", "have", "had",
}


# ==========================================================
# SYNONYM MAP -> canonical word
# ==========================================================
# Used both when a fact is taught and when a question is asked,
# so "who invented python" and "who created python" normalise
# to the same tag and therefore match the same stored fact.

SYNONYMS = {
    "created": "create", "invented": "create", "made": "create",
    "built": "create", "developed": "create", "designed": "create",
    "creator": "create", "inventor": "create", "founder": "create",
    "founded": "create",

    "explain": "about", "describe": "about", "define": "about",
    "definition": "about", "meaning": "about",

    "released": "release", "launched": "release", "published": "release",

    "uses": "use", "using": "use", "used": "use",
}


# ==========================================================
# CODE-ROLE KEYWORDS
# ==========================================================
# When code is taught, we guess which reusable "role" it plays
# so the composer can later pull it back out by purpose.

ROLE_KEYWORDS = {
    "login": ["login", "signin", "sign in", "authenticate", "password"],
    "authentication": ["auth", "token", "jwt", "session", "authorization"],
    "database": ["connect", "cursor", "sqlalchemy", "database", "db.", "query"],
    "file_handling": ["open(", "read()", "write(", "with open"],
    "api_request": ["requests.", "fetch(", "axios", "http.get", "http.post"],
    "sorting": ["sort(", "sorted(", "sort_values"],
    "search": ["search", "find(", "filter("],
    "routing": ["@app.route", "router.", "app.get(", "app.post("],
    "templates": ["render_template", "jinja", ".html"],
}


# ==========================================================
# PROJECT TEMPLATES
# ==========================================================
# Each template lists the "roles" a project of that type
# typically needs. The composer looks these roles up in the
# snippet library.

PROJECT_TEMPLATES = {
    "flask_project": {
        "match": ["flask app", "flask project", "flask website"],
        "roles": ["routing", "templates", "database", "authentication"],
    },
    "django_project": {
        "match": ["django app", "django project"],
        "roles": ["routing", "templates", "database", "authentication"],
    },
    "rest_api": {
        "match": ["rest api", "api project", "backend api"],
        "roles": ["routing", "database", "authentication", "api_request"],
    },
    "cli_application": {
        "match": ["cli app", "command line", "cli tool"],
        "roles": ["file_handling", "search", "sorting"],
    },
    "crud_application": {
        "match": ["crud app", "crud system", "management system"],
        "roles": ["database", "routing", "search", "sorting"],
    },
    "portfolio_website": {
        "match": ["portfolio", "portfolio website", "personal website"],
        "roles": ["routing", "templates"],
    },
}


# ==========================================================
# DEPENDENCY GRAPH DEFAULTS (seed — grows as you teach more)
# ==========================================================

DEFAULT_GRAPH = {
    "flask": ["routing", "templates", "sqlalchemy", "authentication", "sessions"],
    "django": ["models", "views", "templates", "urls", "orm"],
    "python": ["variables", "functions", "loops", "classes"],
    "sql": ["select", "insert", "update", "delete", "joins"],
}


# ==========================================================
# HOW MANY TAUGHT ITEMS = 100% PROGRESS FOR A SUBCATEGORY
# ==========================================================
# There's no objective "complete" for a topic — this is just a
# practical yardstick so the progress command has something to
# show. Change freely.

PROGRESS_TARGET = 10


# ==========================================================
# LOW-LEVEL JSON HELPERS
# ==========================================================

def _ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)


def _load(path, default):
    _ensure_storage()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return default
    return default


def _save(path, data):
    _ensure_storage()
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    except Exception as error:
        print(f"[Knowledge Warning] Could not save {path}: {error}")


# ==========================================================
# CATEGORY TREE
# ==========================================================

def get_category_tree():
    tree = _load(CATEGORIES_FILE, None)
    if tree is None:
        tree = {k: list(v) for k, v in DEFAULT_CATEGORIES.items()}
        _save(CATEGORIES_FILE, tree)
    return tree


def list_categories():
    return list(get_category_tree().keys())


def list_subcategories(category):
    tree = get_category_tree()
    return tree.get(category.lower().strip(), [])


def add_category(name):
    name = name.lower().strip()
    tree = get_category_tree()
    if name not in tree:
        tree[name] = ["other"]
        _save(CATEGORIES_FILE, tree)
    return name


def add_subcategory(category, subcategory):
    category = category.lower().strip()
    subcategory = subcategory.lower().strip()
    tree = get_category_tree()
    tree.setdefault(category, [])
    if subcategory not in tree[category]:
        tree[category].append(subcategory)
        _save(CATEGORIES_FILE, tree)
    return subcategory


# ==========================================================
# TEXT / TAG UTILITIES
# ==========================================================

def _clean_word(word):
    return re.sub(r"[^a-z0-9+#.]", "", word.lower())


def extract_tags(text):
    words = text.split()
    tags = set()

    for word in words:
        cleaned = _clean_word(word)
        if not cleaned or cleaned in STOPWORDS or len(cleaned) < 2:
            continue
        canonical = SYNONYMS.get(cleaned, cleaned)
        tags.add(canonical)

    return tags


# ==========================================================
# CONTENT-TYPE DETECTION
# ==========================================================

CODE_HINTS = [
    "def ", "function ", "class ", "import ", "print(", "console.log",
    "{", "};", "return ", "for (", "for(", "while (", "while(",
    "public class", "#include", "SELECT ", "select ",
]


# Identifier immediately followed by "(" with no space (a real
# function/method call, e.g. "generate_jwt(user)") — deliberately
# NOT allowing a space before "(" so prose like "Python (created
# by Guido)" doesn't false-positive as code.
_FUNCTION_CALL_PATTERN = re.compile(r"[a-zA-Z_][a-zA-Z0-9_.]*\([^()]*\)")

# Identifier, optional [index] or .attr, then a real assignment.
# "=" on its own is a strong code signal — it's rare in prose.
_ASSIGNMENT_PATTERN = re.compile(
    r"[a-zA-Z_][a-zA-Z0-9_]*(\[[^\]]+\]|\.\w+)?\s*=\s*\S+"
)


def detect_type(text):
    lowered = text.lower()

    code_score = sum(1 for hint in CODE_HINTS if hint.lower() in lowered)

    if _FUNCTION_CALL_PATTERN.search(text):
        code_score += 1
    if _ASSIGNMENT_PATTERN.search(text):
        code_score += 1

    has_code_symbols = bool(re.search(r"[(){}\[\];]", text))

    if code_score >= 1 and has_code_symbols:
        return "code"

    if re.search(r"\b(is|was|are|were)\b.+\b(created|invented|made|built|"
                 r"developed|founded|released|located|known)\b", lowered):
        return "fact"

    if len(text.split()) <= 25:
        return "fact"

    return "concept"


# ==========================================================
# CODE ANALYZER
# ==========================================================
# Regex based (language-agnostic-ish). Pulls out structural
# metadata from a taught code snippet: imports, functions,
# classes, loops, conditions, libraries used.

def analyze_code(code_text):
    analysis = {
        "imports": [],
        "functions": [],
        "classes": [],
        "has_loop": bool(re.search(r"\bfor\b|\bwhile\b", code_text)),
        "has_condition": bool(re.search(r"\bif\b", code_text)),
        "libraries": [],
    }

    analysis["imports"] = re.findall(
        r"(?:^|\n)\s*(?:import|from)\s+([a-zA-Z0-9_.]+)", code_text
    )

    analysis["functions"] = re.findall(
        r"(?:def|function)\s+([a-zA-Z0-9_]+)\s*\(", code_text
    )

    analysis["classes"] = re.findall(r"class\s+([a-zA-Z0-9_]+)", code_text)

    analysis["libraries"] = sorted(set(
        lib.split(".")[0] for lib in analysis["imports"]
    ))

    return analysis


def detect_roles(code_text):
    lowered = code_text.lower()
    roles = []

    for role, keywords in ROLE_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            roles.append(role)

    return roles or ["general"]


# ==========================================================
# KNOWLEDGE BASE — READ / WRITE
# ==========================================================
# Structure on disk:
# {
#   "programming & technology": {
#       "python": [ {entry}, {entry}, ... ],
#       ...
#   },
#   ...
# }

def _load_kb():
    return _load(KNOWLEDGE_FILE, {})


def _save_kb(kb):
    _save(KNOWLEDGE_FILE, kb)


def _find_similar(entries, new_tags, threshold=0.7):
    """Returns the index of an existing entry that overlaps
    heavily with new_tags (possible duplicate), else None."""
    for index, entry in enumerate(entries):
        existing_tags = set(entry.get("tags", []))
        if not existing_tags or not new_tags:
            continue
        overlap = len(existing_tags & new_tags) / len(existing_tags | new_tags)
        if overlap >= threshold:
            return index
    return None


def check_duplicate(category, subcategory, text):
    """Call this BEFORE teach() when you want to warn the user
    first. Returns the existing entry dict if a near-duplicate
    is found, else None."""
    category = category.lower().strip()
    subcategory = subcategory.lower().strip()

    kb = _load_kb()
    entries = kb.get(category, {}).get(subcategory, [])

    tags = extract_tags(text)
    index = _find_similar(entries, tags)

    return entries[index] if index is not None else None


def teach(category, subcategory, text, mode="add"):
    """
    mode: "add"     -> just append (used when there's no duplicate,
                        or user chose "keep both")
          "replace"  -> overwrite the most similar existing entry
          "merge"    -> combine text with the most similar entry
    Returns the saved entry dict.
    """
    category = category.lower().strip()
    subcategory = subcategory.lower().strip()
    text = text.strip()

    kb = _load_kb()
    kb.setdefault(category, {})
    kb[category].setdefault(subcategory, [])
    entries = kb[category][subcategory]

    content_type = detect_type(text)
    tags = extract_tags(text)

    entry = {
        "type": content_type,
        "text": text,
        "tags": sorted(tags),
        "date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
    }

    if content_type == "code":
        entry["analysis"] = analyze_code(text)
        entry["roles"] = detect_roles(text)
        _store_snippet(category, subcategory, text, entry["roles"])
        _grow_graph(subcategory, entry["analysis"]["libraries"])

    if mode == "replace":
        index = _find_similar(entries, tags)
        if index is not None:
            entries[index] = entry
        else:
            entries.append(entry)

    elif mode == "merge":
        index = _find_similar(entries, tags)
        if index is not None:
            entries[index]["text"] = entries[index]["text"] + " " + text
            entries[index]["tags"] = sorted(
                set(entries[index]["tags"]) | tags
            )
        else:
            entries.append(entry)

    else:  # "add"
        entries.append(entry)

    _save_kb(kb)
    return entry


def forget(category, subcategory=None):
    """Deletes a whole subcategory's knowledge, or a whole
    category if subcategory is None. Returns True if something
    was removed."""
    category = category.lower().strip()
    kb = _load_kb()

    if category not in kb:
        return False

    if subcategory is None:
        del kb[category]
    else:
        subcategory = subcategory.lower().strip()
        if subcategory not in kb[category]:
            return False
        del kb[category][subcategory]

    _save_kb(kb)
    return True


# ==========================================================
# SNIPPET LIBRARY (code blocks grouped by role)
# ==========================================================

def _store_snippet(category, subcategory, code_text, roles):
    library = _load(SNIPPET_FILE, {})

    for role in roles:
        library.setdefault(role, [])
        library[role].append({
            "code": code_text,
            "category": category,
            "subcategory": subcategory,
            "date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        })

    _save(SNIPPET_FILE, library)


def get_snippets(role):
    library = _load(SNIPPET_FILE, {})
    return library.get(role, [])


# ==========================================================
# DEPENDENCY GRAPH
# ==========================================================

def _load_graph():
    graph = _load(GRAPH_FILE, None)
    if graph is None:
        graph = {k: list(v) for k, v in DEFAULT_GRAPH.items()}
        _save(GRAPH_FILE, graph)
    return graph


def _grow_graph(concept, related_items):
    if not related_items:
        return
    graph = _load_graph()
    concept = concept.lower().strip()
    graph.setdefault(concept, [])
    for item in related_items:
        item = item.lower().strip()
        if item and item not in graph[concept]:
            graph[concept].append(item)
    _save(GRAPH_FILE, graph)


def get_related(concept):
    graph = _load_graph()
    return graph.get(concept.lower().strip(), [])


# ==========================================================
# RETRIEVAL — answer a normal-conversation question using
# whatever has been taught
# ==========================================================

def _score_entry(entry, query_tags):
    entry_tags = set(entry.get("tags", []))
    if not entry_tags or not query_tags:
        return 0
    return len(entry_tags & query_tags)


def search(query, category=None, subcategory=None, limit=5):
    """Returns a list of (score, category, subcategory, entry)
    sorted by best match first. Search is global unless
    category/subcategory narrows it."""
    kb = _load_kb()
    query_tags = extract_tags(query)

    results = []

    categories = [category.lower()] if category else kb.keys()

    for cat in categories:
        if cat not in kb:
            continue
        subcats = [subcategory.lower()] if subcategory else kb[cat].keys()

        for sub in subcats:
            if sub not in kb[cat]:
                continue
            for entry in kb[cat][sub]:
                score = _score_entry(entry, query_tags)
                if score > 0:
                    results.append((score, cat, sub, entry))

    results.sort(key=lambda item: item[0], reverse=True)
    return results[:limit]


# Small set of natural-sounding templates so a stored fact
# doesn't always come back word-for-word.
_ANSWER_TEMPLATES = [
    "{fact}",
    "From what I've learned: {fact}",
    "Here's what I know — {fact}",
]


def answer_query(query):
    """
    Main entry point brain.py should call during normal chat.
    Returns a natural-ish answer string, or None if nothing
    taught matches well enough.
    """
    results = search(query, limit=5)

    if not results:
        return None

    best_score = results[0][0]
    if best_score == 0:
        return None

    # Combine multiple facts if they're about the same
    # subcategory and all matched reasonably well (FEATURE 8)
    top_cat, top_sub = results[0][1], results[0][2]
    combined = [
        entry["text"] for score, cat, sub, entry in results
        if cat == top_cat and sub == top_sub and score == best_score
    ]

    if len(combined) > 1:
        fact_text = " ".join(combined)
    else:
        fact_text = combined[0]

    index = hash(query) % len(_ANSWER_TEMPLATES)
    return _ANSWER_TEMPLATES[index].format(fact=fact_text)


# ==========================================================
# PROJECT PLANNER + COMPOSER
# ==========================================================

def match_template(request_text):
    lowered = request_text.lower()
    for template_name, template in PROJECT_TEMPLATES.items():
        if any(phrase in lowered for phrase in template["match"]):
            return template_name
    return None


def plan_project(request_text):
    """Returns {template, required_roles, available_roles,
    missing_roles} — the 'rule based planner' step."""
    template_name = match_template(request_text)

    if template_name is None:
        return None

    required = PROJECT_TEMPLATES[template_name]["roles"]
    available = [role for role in required if get_snippets(role)]
    missing = [role for role in required if role not in available]

    return {
        "template": template_name,
        "required_roles": required,
        "available_roles": available,
        "missing_roles": missing,
    }


def compose_project(request_text):
    """
    Assembles a project skeleton out of taught snippets.
    Returns a string: either the assembled skeleton, or an
    honest explanation of what's missing so it can be taught.
    """
    plan = plan_project(request_text)

    if plan is None:
        return (
            "I don't have a project template that matches that request yet. "
            "I currently know: " + ", ".join(
                t.replace("_", " ") for t in PROJECT_TEMPLATES
            ) + "."
        )

    if plan["missing_roles"]:
        missing = ", ".join(role.replace("_", " ") for role in plan["missing_roles"])
        return (
            f"I can partially build a {plan['template'].replace('_', ' ')}, "
            f"but I haven't been taught code for: {missing}. "
            "Teach me those first, or I'll only assemble what I already know."
        )

    parts = [f"# Assembled {plan['template'].replace('_', ' ')} "
             f"(built from what you've taught me)\n"]

    for role in plan["required_roles"]:
        snippets = get_snippets(role)
        chosen = snippets[-1]  # most recently taught version of this role
        parts.append(f"\n# --- {role.replace('_', ' ').title()} ---\n{chosen['code']}")

    return "\n".join(parts)


# ==========================================================
# PROGRESS TRACKING
# ==========================================================

def progress_report():
    kb = _load_kb()
    if not kb:
        return "You haven't taught me anything yet."

    lines = []
    for category, subcats in kb.items():
        lines.append(category.title())
        for subcat, entries in subcats.items():
            percent = min(100, int((len(entries) / PROGRESS_TARGET) * 100))
            lines.append(f"  {subcat.title()} — {percent}% ({len(entries)} items taught)")

    return "\n".join(lines)


def what_have_i_learned():
    kb = _load_kb()
    if not kb:
        return "You haven't taught me anything yet."

    total = sum(
        len(entries)
        for subcats in kb.values()
        for entries in subcats.values()
    )

    lines = [f"I've learned {total} things so far, across:"]
    for category, subcats in kb.items():
        subcat_names = ", ".join(subcats.keys())
        lines.append(f"- {category.title()}: {subcat_names}")

    return "\n".join(lines)
