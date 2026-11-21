# ==========================================================
# JARVIS AI
# TRAINING MODE
# Python 3.12
# ==========================================================
#
# Handles the conversation FLOW for teaching Jarvis. The
# actual storage / matching logic lives in knowledge_engine.py
# — this file just manages "what step of teaching are we on".
#
# TWO WAYS TO TEACH:
#
# 1. Step-by-step (this class, TrainingSession):
#       You: training mode
#       Jarvis: [shows category list]
#       You: 1                      (or "programming & technology")
#       Jarvis: [shows subcategory list]
#       You: python
#       Jarvis: "Okay, teach me. Type EXIT when done."
#       You: Python was created by Guido van Rossum.
#       Jarvis: "Got it."
#       You: EXIT
#
# 2. One-line quick teach (quick_teach(), no session needed):
#       teach: python was created by guido van rossum
#       teach [programming & technology/python]: <fact or code>
# ==========================================================

import re
import knowledge_engine as ke


# ==========================================================
# ENTRY / EXIT PHRASES (checked in brain.py)
# ==========================================================

ENTRY_PHRASES = [
    "training mode",
    "start training",
    "teach you something",
    "start teaching",
    "i want to teach you",
    "enter training mode",
]

QUICK_TEACH_PATTERN = re.compile(
    r"^teach(?:\s*\[(?P<path>[^\]]+)\])?\s*:\s*(?P<body>.+)$",
    re.IGNORECASE | re.DOTALL,
)


# ==========================================================
# TRAINING SESSION — one per JarvisBrain instance
# ==========================================================

class TrainingSession:

    def __init__(self):
        self.active = False
        self.stage = None          # category / subcategory / teaching / duplicate_confirm
        self.category = None
        self.subcategory = None
        self._pending_text = None  # text waiting on a duplicate decision

    # ------------------------------------------------------
    def is_active(self):
        return self.active

    # ------------------------------------------------------
    def start(self):
        self.active = True
        self.stage = "category"
        return self._category_menu_text()

    # ------------------------------------------------------
    def _category_menu_text(self):
        categories = ke.list_categories()
        lines = ["Which category do you want to teach me?", ""]
        for index, name in enumerate(categories, start=1):
            lines.append(f"{index}. {name.title()}")
        lines.append("")
        lines.append("Type a number, an existing category name, or a brand new category name.")
        return "\n".join(lines)

    # ------------------------------------------------------
    def _subcategory_menu_text(self):
        subs = ke.list_subcategories(self.category)
        lines = [f"Category: {self.category.title()}", "", "Pick a subcategory:", ""]
        for index, name in enumerate(subs, start=1):
            lines.append(f"{index}. {name.title()}")
        lines.append("")
        lines.append("Type a number, an existing subcategory name, or a new one.")
        return "\n".join(lines)

    # ------------------------------------------------------
    def _resolve_choice(self, text, options):
        """User can type a number OR the name itself."""
        text = text.strip().lower()

        if text.isdigit():
            idx = int(text) - 1
            if 0 <= idx < len(options):
                return options[idx]
            return None

        if text in options:
            return text

        return text  # treat as a brand-new custom name

    # ------------------------------------------------------
    def handle_input(self, text):
        text = text.strip()

        # ---- global exit, works from any stage ----
        if text.upper() == "EXIT" or text.lower() in ["stop training", "exit training"]:
            self.active = False
            self.stage = None
            self.category = None
            self.subcategory = None
            return "Training mode closed. Thanks for teaching me!"

        # ---- stage: choosing category ----
        if self.stage == "category":
            categories = ke.list_categories()
            choice = self._resolve_choice(text, categories)

            if choice is None:
                return "That number isn't in the list. Try again, or type a category name."

            if choice not in categories:
                choice = ke.add_category(choice)

            self.category = choice
            self.stage = "subcategory"
            return self._subcategory_menu_text()

        # ---- stage: choosing subcategory ----
        if self.stage == "subcategory":
            subs = ke.list_subcategories(self.category)
            choice = self._resolve_choice(text, subs)

            if choice is None:
                return "That number isn't in the list. Try again, or type a subcategory name."

            if choice not in subs:
                choice = ke.add_subcategory(self.category, choice)

            self.subcategory = choice
            self.stage = "teaching"
            return (
                f"You can now start teaching me about {self.subcategory.title()}.\n"
                "Send facts, definitions, or code — one at a time.\n"
                "Type EXIT when finished."
            )

        # ---- stage: waiting on a duplicate decision ----
        if self.stage == "duplicate_confirm":
            return self._resolve_duplicate(text)

        # ---- stage: actively teaching ----
        if self.stage == "teaching":
            return self._teach_one(text)

        # Shouldn't normally happen, but fail safe:
        self.active = False
        return "Something went wrong with training mode, so I closed it. Try 'training mode' again."

    # ------------------------------------------------------
    def _teach_one(self, text):
        if not text:
            return "I didn't catch anything to learn there — try again."

        existing = ke.check_duplicate(self.category, self.subcategory, text)

        if existing is not None:
            self._pending_text = text
            self.stage = "duplicate_confirm"
            return (
                "This looks similar to something I already know:\n"
                f"  \"{existing['text']}\"\n\n"
                "Should I Replace it, Merge the two, or Keep Both? "
                "(reply: replace / merge / keep both)"
            )

        ke.teach(self.category, self.subcategory, text, mode="add")
        return "Got it. Teach me more, or type EXIT when done."

    # ------------------------------------------------------
    def _resolve_duplicate(self, answer):
        answer = answer.strip().lower()
        text = self._pending_text
        self._pending_text = None
        self.stage = "teaching"

        if answer in ["replace", "r"]:
            ke.teach(self.category, self.subcategory, text, mode="replace")
            return "Replaced the old entry. Teach me more, or type EXIT when done."

        if answer in ["merge", "m"]:
            ke.teach(self.category, self.subcategory, text, mode="merge")
            return "Merged with the existing entry. Teach me more, or type EXIT when done."

        # default / "keep both"
        ke.teach(self.category, self.subcategory, text, mode="add")
        return "Kept both versions. Teach me more, or type EXIT when done."


# ==========================================================
# QUICK ONE-LINE TEACH (no session / state needed)
# ==========================================================
# Formats:
#   teach: <fact or code>
#   teach [category/subcategory]: <fact or code>
#   teach [subcategory]: <fact or code>     (category = "personal knowledge")

DEFAULT_CATEGORY = "personal knowledge"
DEFAULT_SUBCATEGORY = "other"


def is_quick_teach(command):
    return QUICK_TEACH_PATTERN.match(command) is not None


def quick_teach(command):
    match = QUICK_TEACH_PATTERN.match(command)

    if not match:
        return None

    body = match.group("body").strip()
    path = match.group("path")

    if not body:
        return "Tell me what to learn after the colon, e.g. 'teach: python is a programming language'."

    if path:
        pieces = [p.strip().lower() for p in path.split("/") if p.strip()]
        if len(pieces) >= 2:
            category, subcategory = pieces[0], pieces[1]
        else:
            category, subcategory = DEFAULT_CATEGORY, pieces[0]
    else:
        category, subcategory = DEFAULT_CATEGORY, DEFAULT_SUBCATEGORY

    if category not in ke.list_categories():
        category = ke.add_category(category)
    if subcategory not in ke.list_subcategories(category):
        subcategory = ke.add_subcategory(category, subcategory)

    existing = ke.check_duplicate(category, subcategory, body)
    if existing is not None:
        # Quick-teach has no back-and-forth, so default to "keep both"
        # rather than silently overwrite — matches FEATURE 12's
        # "never silently overwrite" rule.
        ke.teach(category, subcategory, body, mode="add")
        return (
            f"Learned it under {category.title()} / {subcategory.title()} "
            "(kept alongside a similar entry I already had — say "
            "'forget <category>/<subcategory>' if you want to clean it up)."
        )

    ke.teach(category, subcategory, body, mode="add")
    return f"Learned it under {category.title()} / {subcategory.title()}."
