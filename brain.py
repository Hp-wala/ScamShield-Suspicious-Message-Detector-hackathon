# ==========================================================
# JARVIS AI
# BRAIN
# Python 3.12
# Version 5.0
# ==========================================================

import datetime
import re

import nlp_engine
import automation_engine
import triggers
import code_engine
import tech_kb
import knowledge_engine
import training_mode

from config import ENABLE_LLM_FALLBACK
from memory import JarvisMemory

BRAIN_VERSION = "5.0"


HELP_COMMAND_SYNONYMS = [
    "help",
    "help me",
    "commands",
    "show commands",
    "show me commands",
    "list commands",
    "what can you do",
    "features",
    "capabilities",
]

HELP_ENTRIES = [
    {
        "category": "General",
        "name": "Greeting",
        "description": "Greet Jarvis and receive a friendly response.",
        "syntax": "hello | hi | hey | good morning | good afternoon | good evening",
        "parameters": "none",
        "example": "hello",
    },
    {
        "category": "General",
        "name": "Time query",
        "description": "Ask Jarvis for the current time.",
        "syntax": "time",
        "parameters": "none",
        "example": "time",
    },
    {
        "category": "General",
        "name": "Date query",
        "description": "Ask Jarvis for today\'s date.",
        "syntax": "date | today",
        "parameters": "none",
        "example": "date",
    },
    {
        "category": "General",
        "name": "Identity query",
        "description": "Ask Jarvis for its name or identity.",
        "syntax": "your name | what is your name | who are you | tell me your name",
        "parameters": "none",
        "example": "what is your name",
    },
    {
        "category": "General",
        "name": "Help",
        "description": "Show the full list of available commands.",
        "syntax": "help | commands | show commands | what can you do",
        "parameters": "none",
        "example": "help",
    },
    {
        "category": "General",
        "name": "Exit",
        "description": "Close Jarvis and exit the application.",
        "syntax": "exit | quit | shutdown | goodbye | bye",
        "parameters": "none",
        "example": "quit",
    },
    {
        "category": "General",
        "name": "Compound commands",
        "description": "Chain multiple tasks in one sentence using commas or 'and'.",
        "syntax": "open notepad, open calculator | open chrome and check wifi",
        "parameters": "multiple command phrases separated by commas or 'and'",
        "example": "open notepad, open calculator",
    },
    {
        "category": "Dataset & NLP",
        "name": "Dataset search",
        "description": "Search the loaded dataset for matching content.",
        "syntax": "search <keyword> | search for <keyword> | find <keyword> | look for <keyword>",
        "parameters": "keyword",
        "example": "search customer support",
    },
    {
        "category": "Dataset & NLP",
        "name": "Dataset info",
        "description": "Show basic information about the loaded dataset.",
        "syntax": "dataset info | dataset information | show dataset | tell me about dataset",
        "parameters": "none",
        "example": "dataset info",
    },
    {
        "category": "Dataset & NLP",
        "name": "Dataset statistics",
        "description": "Show dataset counts, column details and summary statistics.",
        "syntax": "dataset statistics | dataset stats | statistics | stats",
        "parameters": "none",
        "example": "dataset statistics",
    },
    {
        "category": "Dataset & NLP",
        "name": "Dataset shape",
        "description": "Show the number of rows and columns in the dataset.",
        "syntax": "shape | dataset shape | rows | rows and columns",
        "parameters": "none",
        "example": "shape",
    },
    {
        "category": "Dataset & NLP",
        "name": "Dataset columns",
        "description": "Show the current dataset\'s column names.",
        "syntax": "columns | dataset columns | column names | show dataset columns",
        "parameters": "none",
        "example": "columns",
    },
    {
        "category": "Dataset & NLP",
        "name": "Random sample",
        "description": "Show a random sample of dataset rows.",
        "syntax": "sample tweets | random tweets | show sample",
        "parameters": "none",
        "example": "sample tweets",
    },
    {
        "category": "Dataset & NLP",
        "name": "Clean text",
        "description": "Normalize and clean input text using the NLP engine.",
        "syntax": "clean text <text> | clean <text>",
        "parameters": "text",
        "example": "clean text The quick brown fox!",
    },
    {
        "category": "Dataset & NLP",
        "name": "Tokenize text",
        "description": "Split input text into sentences and words.",
        "syntax": "tokenize text <text> | tokenize <text> | tokenise <text>",
        "parameters": "text",
        "example": "tokenize text Hello world.",
    },
    {
        "category": "Dataset & NLP",
        "name": "Explain topic",
        "description": "Ask Jarvis to explain a technical topic simply or in detail.",
        "syntax": "explain <topic>",
        "parameters": "topic",
        "example": "explain subnetting",
    },
    {
        "category": "Memory",
        "name": "Remember fact",
        "description": "Store a personal fact that Jarvis can recall later.",
        "syntax": "remember my <thing> is <value>",
        "parameters": "thing, value",
        "example": "remember my birthday is 15 August",
    },
    {
        "category": "Memory",
        "name": "Forget fact",
        "description": "Remove a previously remembered personal fact.",
        "syntax": "forget my <thing> | forget <thing>",
        "parameters": "thing",
        "example": "forget my birthday",
    },
    {
        "category": "Memory",
        "name": "Recall fact",
        "description": "Ask Jarvis to recall a fact it has remembered.",
        "syntax": "what is my <thing> | what's my <thing> | when is my <thing>",
        "parameters": "thing",
        "example": "what is my birthday",
    },
    {
        "category": "Memory",
        "name": "Memory summary",
        "description": "Show a summary of Jarvis\'s stored conversation memory.",
        "syntax": "memory",
        "parameters": "none",
        "example": "memory",
    },
    {
        "category": "Memory",
        "name": "Search memory",
        "description": "Search past conversations for a keyword.",
        "syntax": "search memory <keyword>",
        "parameters": "keyword",
        "example": "search memory birthday",
    },
    {
        "category": "Memory",
        "name": "Memory timeline",
        "description": "Display conversation history grouped by date.",
        "syntax": "timeline",
        "parameters": "none",
        "example": "timeline",
    },
    {
        "category": "Memory",
        "name": "Behaviour analysis",
        "description": "Show Jarvis\'s analysis of your interaction style.",
        "syntax": "analyse me | analyze me | behaviour | behavior | what do you know about me",
        "parameters": "none",
        "example": "analyse me",
    },
    {
        "category": "Project & Preferences",
        "name": "Remember project detail",
        "description": "Tell Jarvis what technology your project uses.",
        "syntax": "remember my project uses <tech>",
        "parameters": "tech",
        "example": "remember my project uses python and nltk",
    },
    {
        "category": "Project & Preferences",
        "name": "Project details",
        "description": "Ask Jarvis to describe the current project details it has stored.",
        "syntax": "project details | about this project | tell me about this project",
        "parameters": "none",
        "example": "project details",
    },
    {
        "category": "Project & Preferences",
        "name": "Explanation preference",
        "description": "Set Jarvis\'s explanation style to simple or detailed.",
        "syntax": "prefer simple explanations | explain things simply | prefer detailed explanations | explain things in detail",
        "parameters": "none",
        "example": "prefer detailed explanations",
    },
    {
        "category": "Automation",
        "name": "Open application or path",
        "description": "Open a known app or any valid file/folder path.",
        "syntax": "open <app or file path>",
        "parameters": "app name or filesystem path",
        "example": "open notepad",
    },
    {
        "category": "Automation",
        "name": "Close application",
        "description": "Close a running application by name.",
        "syntax": "close <app>",
        "parameters": "app name",
        "example": "close chrome",
    },
    {
        "category": "Automation",
        "name": "Delete file",
        "description": "Delete a file or empty folder after confirmation.",
        "syntax": "delete file <path>",
        "parameters": "path",
        "example": "delete file C:\\temp\\old.txt",
    },
    {
        "category": "Automation",
        "name": "Volume control",
        "description": "Adjust or mute system volume.",
        "syntax": "volume up | volume down | mute | unmute",
        "parameters": "none",
        "example": "volume up",
    },
    {
        "category": "Automation",
        "name": "Brightness control",
        "description": "Increase or decrease screen brightness.",
        "syntax": "brightness up | brightness down",
        "parameters": "none",
        "example": "brightness down",
    },
    {
        "category": "Automation",
        "name": "Wi-Fi control",
        "description": "Enable or disable Wi-Fi and check its status.",
        "syntax": "wifi on | wifi off | check wifi",
        "parameters": "none",
        "example": "wifi on",
    },
    {
        "category": "Automation",
        "name": "List automation settings",
        "description": "Show the currently supported automation features.",
        "syntax": "list settings | show settings | settings",
        "parameters": "none",
        "example": "list settings",
    },
    {
        "category": "Automation",
        "name": "Schedule a reminder",
        "description": "Create an in-memory reminder for a future time.",
        "syntax": "remind me to <task> in <N> minutes | remind me to <task> at <time>",
        "parameters": "task, relative or absolute time",
        "example": "remind me to stretch in 10 minutes",
    },
    {
        "category": "Automation",
        "name": "List reminders",
        "description": "Show reminders that are currently scheduled.",
        "syntax": "list reminders | show reminders | my reminders",
        "parameters": "none",
        "example": "list reminders",
    },
    {
        "category": "Notifications",
        "name": "Check service notifications",
        "description": "Check WhatsApp or YouTube notifications using a saved Chrome profile.",
        "syntax": "check whatsapp | check youtube",
        "parameters": "none",
        "example": "check whatsapp",
    },
    {
        "category": "Notifications",
        "name": "Chrome profile management",
        "description": "Set or query the named Chrome profile used for notifications.",
        "syntax": "change chrome profile | list chrome profiles | chrome profile | current chrome profile",
        "parameters": "profile name for setting",
        "example": "change chrome profile",
    },
    {
        "category": "Code & Diagnostics",
        "name": "Code snippet lookup",
        "description": "Ask for programming examples in common languages.",
        "syntax": "show me <concept> in <language> | how do I <concept> in <language>",
        "parameters": "concept, language",
        "example": "show me a for loop in python",
    },
    {
        "category": "Code & Diagnostics",
        "name": "Run safe diagnostic commands",
        "description": "Execute supported read-only platform or network checks.",
        "syntax": "run <diagnostic task> now | execute <diagnostic task> now",
        "parameters": "diagnostic task such as ping, list files, disk usage",
        "example": "run ping 8.8.8.8 now",
    },
    {
        "category": "Training & Knowledge",
        "name": "Start training mode",
        "description": "Enter a guided category -> subcategory -> teach loop. Type EXIT to leave.",
        "syntax": "training mode | start training | teach you something",
        "parameters": "none to start; then category, subcategory, and facts one at a time",
        "example": "training mode",
    },
    {
        "category": "Training & Knowledge",
        "name": "Quick one-line teach",
        "description": "Teach a single fact or code snippet without entering the guided flow.",
        "syntax": "teach: <fact or code> | teach [category/subcategory]: <fact or code>",
        "parameters": "fact/code text, optional category/subcategory path",
        "example": "teach [programming & technology/python]: python was created by guido van rossum",
    },
    {
        "category": "Training & Knowledge",
        "name": "What have you learned",
        "description": "List everything taught so far, grouped by category.",
        "syntax": "what have you learned | learned knowledge",
        "parameters": "none",
        "example": "what have you learned",
    },
    {
        "category": "Training & Knowledge",
        "name": "Learning progress",
        "description": "Show a rough percentage of how much has been taught per subcategory.",
        "syntax": "learning progress | knowledge progress | training progress",
        "parameters": "none",
        "example": "learning progress",
    },
    {
        "category": "Training & Knowledge",
        "name": "Forget taught knowledge",
        "description": "Delete everything taught under a category/subcategory.",
        "syntax": "forget <category>/<subcategory>",
        "parameters": "category, subcategory",
        "example": "forget programming & technology/python",
    },
    {
        "category": "Training & Knowledge",
        "name": "Build a project from taught code",
        "description": "Assemble a project skeleton from code snippets you've already taught, using a rule-based template + planner (no LLM). Tells you what's missing if it can't fully build it.",
        "syntax": "build a <project type>",
        "parameters": "project type such as flask app, rest api, cli app, crud system",
        "example": "build a flask app",
    },
]


# ==========================================================
# JARVIS BRAIN
# ==========================================================

class JarvisBrain:

    # ======================================================
    # INITIALIZE
    # ======================================================

    def __init__(self):
        print("=" * 60)
        print("Initializing Brain...")
        print("=" * 60)

        nlp_engine.initialize_nlp()

        # ==============================================
        # MEMORY ENGINE
        # ==============================================
        self.memory = JarvisMemory()

        # ==============================================
        # PENDING CONFIRMATION (for risky automation
        # actions like deleting a file or toggling Wi-Fi)
        # ==============================================
        self.pending_action = None

        # ==============================================
        # TRAINING MODE SESSION (Knowledge-Based Learning)
        # ==============================================
        self.training = training_mode.TrainingSession()

        print("Memory Ready.")
        print("Brain Ready.")
        print("=" * 60)

    # ======================================================
    # CURRENT TIME
    # ======================================================

    def current_time(self):
        return datetime.datetime.now().strftime("%I:%M %p")

    # ======================================================
    # CURRENT DATE
    # ======================================================

    def current_date(self):
        return datetime.datetime.now().strftime("%d %B %Y")

    # ======================================================
    # PRINT SEARCH RESULT
    # ======================================================

    def show_results(self, dataframe):
        print()
        print("=" * 60)
        print("SEARCH RESULT")
        print("=" * 60)
        print(dataframe.head(10))
        print("=" * 60)

    # ======================================================
    # SPLIT A COMPOUND COMMAND INTO SUBTASKS
    # ======================================================
    # Lets the user chain multiple commands in one line, e.g.:
    #   "open notepad , open calculator"
    #   "open chrome and check wifi"
    # Splits on commas first, then on "and" / "then" between
    # remaining parts. Returns a list of trimmed subtask strings.

    def split_into_subtasks(self, command):
        parts = re.split(r"\s*,\s*", command)

        expanded = []
        for part in parts:
            subparts = re.split(r"\s+(?:and then|then|and)\s+", part)
            expanded.extend(sub.strip() for sub in subparts)

        return [part for part in expanded if part]

    # ======================================================
    # EXECUTE A COMPOUND COMMAND AS A TASK LIST
    # ======================================================
    # Prints the plan up front (entry point), runs each subtask
    # through get_response, reports Completed/Failed per task, then
    # returns a single summary as the final response (exit point) —
    # this is the "list to-dos, mark each completed" behaviour.

    FAILURE_PREFIXES = (
        "i don't know", "i couldn't", "i can't", "couldn't",
        "sorry, i don't understand", "please tell me", "please provide",
    )

    def execute_task_list(self, subtasks):
        print()
        print("=" * 60)
        print("TASK LIST")
        print("=" * 60)
        for index, task in enumerate(subtasks, start=1):
            print(f"{index}. {task}")
        print("=" * 60)

        summary_lines = []

        for index, task in enumerate(subtasks, start=1):
            outcome = self.get_response(task)
            failed = outcome.lower().startswith(self.FAILURE_PREFIXES)
            status = "Failed" if failed else "Completed"

            print(f"Task {index} {status}: {task} -> {outcome}")
            summary_lines.append(f"Task {index} ({task}): {status}.")

        print("=" * 60)

        return "\n".join(summary_lines)

    # ======================================================
    # CHECK PREFIX
    # ======================================================

    def starts_with(self, command, words):
        for word in words:
            if command.startswith(word):
                return True
        return False

    # ======================================================
    # REMOVE PREFIX
    # ======================================================

    def remove_prefix(self, command, prefix):
        return command.replace(prefix, "", 1).strip()

    # ======================================================
    # HELP OUTPUT
    # ======================================================

    def print_help(self):
        print()
        print("=" * 60)
        print(f"AVAILABLE COMMANDS - Jarvis AI Version {BRAIN_VERSION}")
        print("=" * 60)

        current_category = None
        for entry in HELP_ENTRIES:
            if entry["category"] != current_category:
                current_category = entry["category"]
                print()
                print(current_category)
                print("-" * len(current_category))

            print(f"{entry['name']}")
            print(f"  Description: {entry['description']}")
            print(f"  Syntax    : {entry['syntax']}")
            print(f"  Parameters: {entry['parameters']}")
            print(f"  Example   : {entry['example']}")
            print()

        self.print_dynamic_diagnostics()
        self.print_dynamic_automation()

        print("=" * 60)

    def print_dynamic_diagnostics(self):
        print()
        print("Code & Diagnostics")
        print("-" * len("Code & Diagnostics"))
        print("Run code snippets with natural language phrases like 'show me a for loop in python'.")
        print("Run safe diagnostics with phrases like 'run ping 8.8.8.8 now'.")
        print("Supported diagnostics:")

        for task, phrases in code_engine.PLATFORM_TASK_KEYWORDS.items():
            sample = phrases[0] if phrases else task
            if task in code_engine.HOST_TASKS:
                sample = sample.replace("<host>", "8.8.8.8")
            print(f"- {task.replace('_', ' ')}: example '{sample}'")

        print()
        print("Supported code concepts:")
        for concept, phrases in code_engine.CONCEPT_KEYWORDS.items():
            sample = phrases[0] if phrases else concept
            print(f"- {concept.replace('_', ' ')}: example '{sample} in python' or '{sample} in javascript'" )

    def print_dynamic_automation(self):
        print()
        print("Automation")
        print("-" * len("Automation"))
        apps = sorted(automation_engine.KNOWN_APPS.keys())
        print("Open a known application with: open <app name>.")
        print(f"Known apps: {', '.join(apps)}")
        print("Close any running app with: close <app name>.")
        print("Open a file or folder with: open <path>.")
        print("Delete a file or empty folder with: delete file <path>.")
        print("Adjust volume with: volume up | volume down | mute.")
        print("Adjust screen brightness with: brightness up | brightness down.")
        print("Control Wi-Fi with: wifi on | wifi off | check wifi.")
        print("Manage reminders with: remind me to <task> in <N> minutes | remind me to <task> at <time>.")
        print("Check notifications with: check whatsapp | check youtube.")
        print("Manage Chrome profiles with: change chrome profile | list chrome profiles | current chrome profile.")

    # ======================================================
    # SAVE MEMORY HELPER
    # ======================================================

    def save_memory(self, command, response):
        try:
            self.memory.remember(command, response)
        except Exception as error:
            # Memory failure should never break the brain's response.
            print(f"[Memory Warning] Could not save memory: {error}")

    # ======================================================
    # EXECUTE A CONFIRMED PENDING ACTION
    # ======================================================

    def _execute_pending_action(self):
        action = self.pending_action

        if action["type"] == "delete_path":
            return automation_engine.delete_path(action["path"])

        if action["type"] == "wifi":
            return automation_engine.wifi_toggle(action["turn_on"])

        return "I lost track of what I was supposed to confirm. Please try again."

    # ======================================================
    # MAIN RESPONSE
    # ======================================================

    def get_response(self, command):

        # ----------------------------------------------
        # Keep the original-case text around for Training Mode
        # (taught facts/code should keep proper capitalization —
        # class names, "Guido van Rossum", etc. — even though
        # every other command in this file matches on the
        # lowercased version below).
        # ----------------------------------------------
        original_command = command.strip()

        # ----------------------------------------------
        # Normalize command
        # ----------------------------------------------
        command = command.lower()
        command = " ".join(command.split())

        if command == "":
            response = "I didn't hear anything."
            self.save_memory(command, response)
            return response

        # ----------------------------------------------
        # Resolve a pending confirmation first, if one
        # is waiting (e.g. "delete file X? yes/no")
        # ----------------------------------------------
        if self.pending_action is not None:
            if self.pending_action["type"] == "set_chrome_profile":
                response = automation_engine.set_active_chrome_profile(command)
                self.pending_action = None
                self.save_memory(command, response)
                return response

            if command in ["yes", "y", "confirm", "confirmed"]:
                response = self._execute_pending_action()
                self.pending_action = None
                self.save_memory(command, response)
                return response

            if command in ["no", "n", "cancel"]:
                self.pending_action = None
                response = "Okay, cancelled."
                self.save_memory(command, response)
                return response

            # Anything else drops the pending action and the
            # command below is processed normally instead.
            self.pending_action = None

        # ----------------------------------------------
        # TRAINING MODE — if a session is already active,
        # every message goes straight to it (category picks,
        # taught facts, EXIT, duplicate replace/merge/keep
        # both). This runs BEFORE compound-split/triggers so
        # teaching text with commas or "and" isn't mangled.
        # ----------------------------------------------
        if self.training.is_active():
            # category/subcategory picks and EXIT are case-insensitive
            # anyway, but taught facts/code keep their original case.
            input_text = original_command if self.training.stage in (
                "teaching", "duplicate_confirm"
            ) else command
            response = self.training.handle_input(input_text)
            self.save_memory(command, response)
            return response

        # ----------------------------------------------
        # TRAINING MODE — entry phrases
        # ----------------------------------------------
        if command in training_mode.ENTRY_PHRASES:
            response = self.training.start()
            self.save_memory(command, response)
            return response

        # ----------------------------------------------
        # TRAINING MODE — quick one-line teach, e.g.
        # "teach: python was created by guido van rossum"
        # "teach [programming & technology/python]: ..."
        # ----------------------------------------------
        if training_mode.is_quick_teach(command):
            response = training_mode.quick_teach(original_command)
            self.save_memory(command, response)
            return response

        # ----------------------------------------------
        # KNOWLEDGE BASE — status commands
        # ----------------------------------------------
        if command in ["what have you learned", "what have i taught you", "learned knowledge"]:
            response = knowledge_engine.what_have_i_learned()
            self.save_memory(command, response)
            return response

        if command in ["learning progress", "knowledge progress", "training progress"]:
            response = knowledge_engine.progress_report()
            self.save_memory(command, response)
            return response

        if self.starts_with(command, ["forget category ", "forget "]) and "/" in command:
            path = command.split(" ", 1)[-1] if command.startswith("forget ") else command
            path = self.remove_prefix(command, "forget category") if command.startswith("forget category") else self.remove_prefix(command, "forget")
            pieces = [p.strip() for p in path.split("/") if p.strip()]
            if len(pieces) >= 2:
                removed = knowledge_engine.forget(pieces[0], pieces[1])
            else:
                removed = knowledge_engine.forget(pieces[0]) if pieces else False
            response = "Forgotten." if removed else "I didn't have anything saved there."
            self.save_memory(command, response)
            return response

        if self.starts_with(command, ["build a ", "build me a ", "create a project"]):
            response = knowledge_engine.compose_project(command)
            self.save_memory(command, response)
            return response

        # ----------------------------------------------
        # Compound command: "open notepad , open calculator"
        # Only when there are 2+ chained parts — a single command
        # falls through to normal processing below.
        # ----------------------------------------------
        subtasks = self.split_into_subtasks(command)

        if len(subtasks) > 1:
            response = self.execute_task_list(subtasks)
            self.save_memory(command, response)
            return response

        # ----------------------------------------------
        # Trigger-based responses (random block, no repeat)
        # ----------------------------------------------
        trigger_response = triggers.check_triggers(command)

        if trigger_response is not None:
            self.save_memory(command, trigger_response)
            return trigger_response

        # ----------------------------------------------
        # Code generation (language / OS / networking)
        # ----------------------------------------------
        executed_response = code_engine.try_execute(command)

        if executed_response is not None:
            self.save_memory(command, executed_response)
            return executed_response

        code_response = code_engine.get_code_response(command)

        if code_response is not None:
            self.save_memory(command, code_response)
            return code_response

        # ----------------------------------------------
        # Passive mood detection (runs on every message)
        # ----------------------------------------------
        detected_mood = None

        try:
            detected_mood = self.memory.detect_mood(command)
        except Exception:
            pass

        # ==================================================
        # MOOD STATEMENT ACKNOWLEDGEMENT
        # ==================================================
        # Handles things like "I am tired today" or "I'm stressed"
        # directly, BEFORE the generic date/time keyword checks
        # further below — otherwise a word like "today" inside the
        # sentence gets misread as a date query instead of a mood
        # statement.
        if detected_mood and re.match(r"^(i am|i'm|feeling|i feel)\b", command):
            mood_responses = {
                "tired": "I hear you. Try to take a short break when you can.",
                "happy": "That's wonderful to hear!",
                "sad": (
                    "I'm sorry you're feeling that way. I'm here if you "
                    "want to talk or need help with something."
                ),
                "stressed": (
                    "Take a deep breath. Let me know how I can help "
                    "lighten the load."
                ),
                "busy": "Got it, I'll keep things quick and efficient.",
            }

            response = mood_responses.get(
                detected_mood,
                "Thanks for sharing. I've noted that.",
            )

            self.save_memory(command, response)
            return response

        # ==================================================
        # CLEAN TEXT
        # ==================================================
        if self.starts_with(command, ["clean text", "clean"]):

            if command.startswith("clean text"):
                text = self.remove_prefix(command, "clean text")
            else:
                text = self.remove_prefix(command, "clean")

            if text == "":
                response = "Please provide some text to clean."
                self.save_memory(command, response)
                return response

            cleaned = nlp_engine.clean_text(text)

            print()
            print("=" * 60)
            print("TEXT CLEANING")
            print("=" * 60)
            print("Original :")
            print(text)
            print()
            print("Cleaned :")
            print(cleaned)
            print("=" * 60)

            response = "Text cleaned successfully."
            self.save_memory(command, response)
            return response

        # ==================================================
        # TOKENIZATION
        # ==================================================
        if self.starts_with(command, ["tokenize text", "tokenise", "tokenize"]):

            if command.startswith("tokenize text"):
                text = self.remove_prefix(command, "tokenize text")
            elif command.startswith("tokenise"):
                text = self.remove_prefix(command, "tokenise")
            else:
                text = self.remove_prefix(command, "tokenize")

            if text == "":
                response = "Please provide some text to tokenize."
                self.save_memory(command, response)
                return response

            output = nlp_engine.preprocess_text(text)

            print()
            print("=" * 60)
            print("TOKENIZATION")
            print("=" * 60)
            print(output)
            print("=" * 60)

            response = "Tokenization completed."
            self.save_memory(command, response)
            return response

        # ==================================================
        # AUTOMATION: NOTIFICATION CHECK (EXPERIMENTAL)
        # ==================================================
        # Matches "check whatsapp", "check whatsapp for messages",
        # "open whatsapp check for message", "check youtube for
        # notifications" — any check/open command mentioning a known
        # service. See automation_engine.check_notifications for the
        # (fragile, best-effort) implementation notes.
        notification_match = re.search(r"\b(whatsapp|youtube)\b", command)

        if notification_match and self.starts_with(command, ["check", "open"]):
            service = notification_match.group(1)
            response = automation_engine.check_notifications(service)
            self.save_memory(command, response)
            return response

        # ==================================================
        # AUTOMATION: CHROME PROFILE (used by notification checks)
        # ==================================================
        # "set chrome profile jarvis" — set it directly by name
        profile_set_match = re.match(
            r"^(?:set|change|switch)\s+chrome\s+profile\s+(?:to\s+)?(.+)$",
            command,
        )

        if profile_set_match:
            name = profile_set_match.group(1).strip()
            response = automation_engine.set_active_chrome_profile(name)
            self.save_memory(command, response)
            return response

        # "change chrome profile" — no name given, ask for one
        if command in ["change chrome profile", "switch chrome profile", "set chrome profile"]:
            existing_profiles = automation_engine.list_chrome_profiles()
            self.pending_action = {"type": "set_chrome_profile"}

            if existing_profiles:
                response = (
                    "What should the new profile be called? "
                    "Saved profiles so far: " + ", ".join(existing_profiles)
                )
            else:
                response = "What should the new Chrome profile be called?"

            self.save_memory(command, response)
            return response

        if command in ["list chrome profiles", "show chrome profiles", "chrome profiles"]:
            profiles = automation_engine.list_chrome_profiles()
            active = automation_engine.get_active_chrome_profile()

            if not profiles:
                response = "No Chrome profiles have been created yet."
            else:
                lines = [
                    f"- {name}" + (" (active)" if name == active else "")
                    for name in profiles
                ]
                response = "Saved Chrome profiles:\n" + "\n".join(lines)

            self.save_memory(command, response)
            return response

        if command in ["current chrome profile", "chrome profile"]:
            active = automation_engine.get_active_chrome_profile()
            response = (
                f"The active Chrome profile is '{active}'."
                if active
                else "No Chrome profile has been set up yet."
            )
            self.save_memory(command, response)
            return response

        # ==================================================
        # AUTOMATION: CLOSE APP (generic, any app)
        # ==================================================
        if command.startswith("close "):
            target = self.remove_prefix(command, "close")

            if target == "":
                response = "Please tell me what to close."
            else:
                response = automation_engine.close_app(target)

            self.save_memory(command, response)
            return response

        # ==================================================
        # AUTOMATION: CHECK WI-FI STATUS (read-only)
        # ==================================================
        if command in ["check wifi", "wifi status", "is wifi on", "check wifi status"]:
            response = automation_engine.check_wifi_status()
            self.save_memory(command, response)
            return response

        # ==================================================
        # AUTOMATION: LIST SETTINGS / CAPABILITIES
        # ==================================================
        if command in ["list settings", "list all settings", "show settings", "settings"]:
            response = automation_engine.list_settings()
            self.save_memory(command, response)
            return response

        # ==================================================
        # AUTOMATION: OPEN APP / FILE / FOLDER
        # ==================================================
        if command.startswith("open "):
            target = self.remove_prefix(command, "open")

            if target == "":
                response = "Please tell me what to open."
            elif target in automation_engine.KNOWN_APPS:
                response = automation_engine.open_app(target)
            else:
                response = automation_engine.open_path(target)

            self.save_memory(command, response)
            return response

        # ==================================================
        # AUTOMATION: DELETE FILE (needs confirmation)
        # ==================================================
        if command.startswith("delete file"):
            path = self.remove_prefix(command, "delete file").strip()

            if path == "":
                response = "Please tell me which file to delete."
            else:
                self.pending_action = {"type": "delete_path", "path": path}
                response = f"Are you sure you want to delete '{path}'? Reply yes or no."

            self.save_memory(command, response)
            return response

        # ==================================================
        # AUTOMATION: VOLUME CONTROL
        # ==================================================
        if command in ["volume up", "increase volume", "volume increase"]:
            response = automation_engine.volume_up()
            self.save_memory(command, response)
            return response

        if command in ["volume down", "decrease volume", "volume decrease"]:
            response = automation_engine.volume_down()
            self.save_memory(command, response)
            return response

        if command in ["mute", "unmute", "volume mute", "mute volume"]:
            response = automation_engine.volume_mute()
            self.save_memory(command, response)
            return response

        # ==================================================
        # AUTOMATION: BRIGHTNESS CONTROL
        # ==================================================
        if command in ["brightness up", "increase brightness"]:
            response = automation_engine.brightness_up()
            self.save_memory(command, response)
            return response

        if command in ["brightness down", "decrease brightness"]:
            response = automation_engine.brightness_down()
            self.save_memory(command, response)
            return response

        # ==================================================
        # AUTOMATION: WI-FI TOGGLE (needs confirmation)
        # ==================================================
        if command in ["wifi on", "turn on wifi", "enable wifi"]:
            self.pending_action = {"type": "wifi", "turn_on": True}
            response = "Are you sure you want to turn Wi-Fi on? Reply yes or no."
            self.save_memory(command, response)
            return response

        if command in ["wifi off", "turn off wifi", "disable wifi"]:
            self.pending_action = {"type": "wifi", "turn_on": False}
            response = "Are you sure you want to turn Wi-Fi off? Reply yes or no."
            self.save_memory(command, response)
            return response

        # ==================================================
        # AUTOMATION: REMINDERS / SCHEDULED TASKS
        # ==================================================
        reminder_match = re.match(r"^remind me to (.+?) (in .+|at .+)$", command)

        if reminder_match:
            task = reminder_match.group(1).strip()
            time_phrase = reminder_match.group(2).strip()

            if time_phrase.startswith("in"):
                delay = automation_engine.parse_relative_delay_seconds(time_phrase)
            else:
                delay = automation_engine.parse_absolute_delay_seconds(time_phrase[2:].strip())

            if delay is None:
                response = (
                    "I couldn't understand that time. Try 'in 10 minutes' "
                    "or 'at 5:30 pm'."
                )
            else:
                automation_engine.schedule_reminder(
                    task, delay, automation_engine.reminder_callback
                )
                minutes = max(int(delay // 60), 0)
                response = f"Okay, I'll remind you to {task} in about {minutes} minute(s)."

            self.save_memory(command, response)
            return response

        if command in ["list reminders", "show reminders", "my reminders"]:
            reminders = automation_engine.list_reminders()

            if not reminders:
                response = "You have no active reminders."
            else:
                lines = [f"- {entry['message']} at {entry['time']}" for entry in reminders]
                response = "Your reminders:\n" + "\n".join(lines)

            self.save_memory(command, response)
            return response

        # ==================================================
        # PROJECT MEMORY
        # ==================================================
        # Examples:
        #   remember my project uses python 3.12
        #   remember project uses nltk, machine learning
        project_remember_match = re.match(
            r"^remember\s+(?:my\s+)?project\s+uses\s+(.+)$",
            command,
        )

        if project_remember_match:
            value = project_remember_match.group(1).strip()
            response = self.memory.remember_project("technology", value)
            self.save_memory(command, response)
            return response

        project_info_commands = [
            "what technology does this project use",
            "what technology does my project use",
            "what does this project use",
            "what does my project use",
            "project details",
            "about this project",
            "tell me about this project",
        ]

        if command in project_info_commands:
            response = self.memory.project_summary()
            self.save_memory(command, response)
            return response

        # ==================================================
        # REMEMBER A FACT
        # ==================================================
        # Examples:
        #   remember my birthday is 15 august
        #   remember my project name is jarvis ai
        if command.startswith("remember"):
            text = self.remove_prefix(command, "remember")
            text = re.sub(r"^that\s+", "", text)

            match = re.match(r"^(?:my\s+)?(.+?)\s+is\s+(.+)$", text)

            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                response = self.memory.remember_fact(key, value)
            else:
                response = (
                    "Please tell me what to remember, like "
                    "'remember my birthday is 15 August'."
                )

            self.save_memory(command, response)
            return response

        # ==================================================
        # FORGET A FACT
        # ==================================================
        # Examples:
        #   forget my birthday
        #   forget birthday
        if command.startswith("forget"):
            text = self.remove_prefix(command, "forget")
            text = re.sub(r"^(?:my\s+|about\s+)", "", text).strip()

            if text == "":
                response = "Please tell me what to forget."
            else:
                response = self.memory.forget_fact(text)

            self.save_memory(command, response)
            return response

        # ==================================================
        # RECALL A FACT
        # ==================================================
        # Examples:
        #   what is my birthday
        #   what's my project name
        #   when is my birthday
        recall_match = re.match(
            r"^(?:what is|what's|when is|tell me)\s+(?:my\s+|the\s+)?(.+?)\??$",
            command,
        )

        if recall_match:
            key = recall_match.group(1).strip()
            value = self.memory.get_fact(key)

            if value:
                response = f"Your {key} is {value}."
                self.save_memory(command, response)
                return response

            # No fact matched — fall through so built-in commands like
            # "what is your name" still get handled further below.

        # ==================================================
        # PREFERENCE MEMORY
        # ==================================================
        preference_commands = {
            "prefer simple explanations": ("explanation_style", "simple"),
            "prefer detailed explanations": ("explanation_style", "detailed"),
            "explain things simply": ("explanation_style", "simple"),
            "explain things in detail": ("explanation_style", "detailed"),
        }

        if command in preference_commands:
            key, value = preference_commands[command]
            self.memory.set_preference(key, value)

            response = f"Got it, I'll use {value} explanations from now on."
            self.save_memory(command, response)
            return response

        # ==================================================
        # EXPLAIN (uses the preference above)
        # ==================================================
        # Common aliases so "explain http" / "explain tls" / etc. match
        # the actual keys used in tech_kb.py, without needing the exact
        # key name typed out.
        TECH_TOPIC_ALIASES = {
            "osi": "osi_model", "osi model": "osi_model",
            "tcp/ip": "tcp_ip_model", "tcp ip": "tcp_ip_model",
            "ip": "ip_addressing", "ipv4": "ip_addressing",
            "ipv6": "ip_addressing", "subnetting": "ip_addressing",
            "cidr": "ip_addressing", "ip address": "ip_addressing",
            "http": "http_https", "https": "http_https",
            "tls": "tls_ssl", "ssl": "tls_ssl",
            "rest": "rest_apis", "rest api": "rest_apis",
            "restful": "rest_apis", "restful api": "rest_apis",
            "dhcp": "dhcp", "dns": "dns", "tcp": "tcp", "udp": "udp",
            "data structures": "data_structures_algorithms",
            "algorithms": "data_structures_algorithms",
            "dsa": "data_structures_algorithms",
            "os": "operating_systems", "operating system": "operating_systems",
            "database": "databases", "db": "databases",
            "distributed system": "distributed_systems",
            "design pattern": "design_patterns",
            "system design": "system_design",
        }

        def _tech_lookup(raw_topic):
            key = raw_topic.strip().lower()
            key = TECH_TOPIC_ALIASES.get(key, key)
            key = key.replace(" ", "_").replace("/", "_")

            entry = tech_kb.get_network_topic(key)
            if entry is not None and entry.get("purpose") is not None:
                return "network", key, entry

            entry = tech_kb.get_cs_topic(key)
            if entry is not None and entry.get("overview") is not None:
                return "cs", key, entry

            return None, None, None

        if command.startswith("explain"):
            topic = self.remove_prefix(command, "explain").strip()

            if topic == "":
                response = "Please tell me what to explain."
                self.save_memory(command, response)
                return response

            style = self.memory.get_preference("explanation_style", "simple")

            kb_kind, kb_key, kb_entry = _tech_lookup(topic)

            if kb_entry is not None:
                display_name = kb_key.replace("_", " ")

                if style == "detailed":
                    lines = [f"{display_name.upper()}", ""]

                    for field, value in kb_entry.items():
                        if value is None:
                            continue
                        label = field.replace("_", " ").capitalize()
                        lines.append(f"{label}:\n{value}\n")

                    response = "\n".join(lines).strip()
                else:
                    summary_field = "purpose" if kb_kind == "network" else "overview"
                    examples = kb_entry.get("examples") or kb_entry.get("common_patterns")

                    response = f"{kb_entry[summary_field]}"

                    if examples:
                        response += f"\n\nExample: {examples}"

                    response += (
                        "\n\nSay 'prefer detailed explanations' for the full "
                        "technical breakdown (architecture, security, best "
                        "practices, etc.)."
                    )

                self.save_memory(command, response)
                return response

            # ----------------------------------------------
            # Fallback: topic isn't in tech_kb.py yet, use the
            # old generic template so Jarvis still says something.
            # ----------------------------------------------
            if style == "detailed":
                response = (
                    f"{topic.capitalize()} is a broad topic — it has a core "
                    f"definition, how it works internally, common techniques, "
                    f"and real-world applications. Let me know which part "
                    f"you'd like me to go deeper on."
                )
            else:
                response = (
                    f"In simple terms, {topic} is something you can picture "
                    f"with an everyday example rather than technical jargon. "
                    f"Say 'prefer detailed explanations' if you want more depth."
                )

            self.save_memory(command, response)
            return response

        # ==================================================
        # MEMORY TIMELINE
        # ==================================================
        if command == "timeline":
            grouped = self.memory.timeline()

            if not grouped:
                response = "No conversation history yet."
                self.save_memory(command, response)
                return response

            print()
            print("=" * 60)
            print("MEMORY TIMELINE")
            print("=" * 60)

            for date_part, entries in grouped.items():
                print(f"\n{date_part}")
                for time_part, user_msg, jarvis_msg in entries:
                    print(f"  {time_part}  You    : {user_msg}")
                    print(f"            Jarvis : {jarvis_msg}")

            print()
            print("=" * 60)

            response = "Timeline displayed."
            self.save_memory(command, response)
            return response

        # ==================================================
        # SEARCH MEMORY (past conversations)
        # ==================================================
        # Must be checked before the generic dataset "search" prefix.
        if command.startswith("search memory"):
            keyword = self.remove_prefix(command, "search memory").strip()

            if keyword == "":
                response = "Please tell me what to search for in memory."
                self.save_memory(command, response)
                return response

            matches = self.memory.search_memory(keyword)

            if not matches:
                response = (
                    f"I couldn't find anything about '{keyword}' "
                    f"in our past conversations."
                )
                self.save_memory(command, response)
                return response

            print()
            print("=" * 60)
            print("MEMORY SEARCH RESULTS")
            print("=" * 60)

            for entry in matches[-10:]:
                print(f"[{entry['time']}] You    : {entry['user']}")
                print(f"           Jarvis : {entry['jarvis']}")
                print()

            print("=" * 60)

            response = f"I found {len(matches)} matching memories."
            self.save_memory(command, response)
            return response

        # ==================================================
        # SEARCH DATASET
        # ==================================================
        search_prefix = None
        prefixes = ["search for", "search", "find", "look for"]

        for prefix in prefixes:
            if command.startswith(prefix):
                search_prefix = prefix
                break

        if search_prefix is not None:
            keyword = self.remove_prefix(command, search_prefix)
            keyword = " ".join(keyword.split())

            if keyword == "":
                response = "Please tell me what to search."
                self.save_memory(command, response)
                return response

            results = nlp_engine.search_dataset(keyword)

            if len(results) == 0:
                response = f"No results found for '{keyword}'."
                self.save_memory(command, response)
                return response

            self.show_results(results)

            response = f"I found {len(results)} matching tweets."
            self.save_memory(command, response)
            return response

        # ==================================================
        # DATASET INFORMATION
        # ==================================================
        dataset_info_commands = [
            "dataset info",
            "dataset information",
            "show dataset",
            "show dataset information",
            "information about dataset",
            "tell me about dataset",
        ]

        if command in dataset_info_commands:
            nlp_engine.dataset_info()
            response = "Dataset information displayed."
            self.save_memory(command, response)
            return response

        # ==================================================
        # DATASET STATISTICS
        # ==================================================
        dataset_statistics_commands = [
            "dataset statistics",
            "dataset stats",
            "statistics",
            "stats",
            "show statistics",
            "show dataset statistics",
        ]

        if command in dataset_statistics_commands:
            nlp_engine.dataset_statistics()
            response = "Dataset statistics displayed."
            self.save_memory(command, response)
            return response

        # ==================================================
        # DATASET SHAPE
        # ==================================================
        shape_commands = [
            "shape",
            "dataset shape",
            "shape of dataset",
            "rows",
            "rows and columns",
        ]

        if command in shape_commands:
            rows, columns = nlp_engine.get_shape()
            response = f"The dataset contains {rows} rows and {columns} columns."
            self.save_memory(command, response)
            return response

        # ==================================================
        # DATASET COLUMNS
        # ==================================================
        column_commands = [
            "columns",
            "dataset columns",
            "column names",
            "columns names",
            "show columns",
            "show dataset columns",
        ]

        if command in column_commands:
            columns = nlp_engine.get_columns()

            print()
            print("=" * 60)
            print("DATASET COLUMNS")
            print("=" * 60)
            for column in columns:
                print(column)
            print("=" * 60)

            response = "Dataset column names displayed."
            self.save_memory(command, response)
            return response

        # ==================================================
        # RANDOM SAMPLE
        # ==================================================
        sample_commands = [
            "sample",
            "sample tweets",
            "random tweets",
            "show sample",
            "show random tweets",
        ]

        if command in sample_commands:
            print()
            print("=" * 60)
            print("RANDOM TWEETS")
            print("=" * 60)
            print(nlp_engine.random_tweets(5))
            print("=" * 60)

            response = "Random tweets displayed."
            self.save_memory(command, response)
            return response

        # ==================================================
        # MEMORY SUMMARY
        # ==================================================
        if command == "memory":
            response = str(self.memory.summary())
            self.save_memory(command, response)
            return response

        # ==================================================
        # BEHAVIOUR ANALYSIS
        # ==================================================
        behaviour_commands = [
            "analyse me",
            "analyze me",
            "behaviour",
            "behavior",
            "what do you know about me",
            "analyze my behaviour",
            "my profile",
        ]

        if command in behaviour_commands:
            response = self.memory.analyse_behaviour()
            self.save_memory(command, response)
            return response

        # ==================================================
        # GREETINGS (mood + name aware)
        # ==================================================
        greetings = [
            "hello",
            "hi",
            "hey",
            "good morning",
            "good afternoon",
            "good evening",
        ]

        if any(word in command for word in greetings):
            name = self.memory.user_profile.get("name")
            mood = self.memory.get_mood()

            greeting_line = f"Hello {name}." if name else "Hello."

            mood_notes = {
                "tired": " Hope you get some rest soon.",
                "stressed": " Take it easy, I'm here to help.",
                "sad": " Hope your day gets better.",
                "happy": " Glad to hear you're doing well!",
                "busy": " Let's get through your tasks quickly.",
            }

            greeting_line += mood_notes.get(mood, "")
            greeting_line += " How can I help you today?"

            response = greeting_line
            self.save_memory(command, response)
            return response

        # ==================================================
        # NAME
        # ==================================================
        name_commands = [
            "your name",
            "what is your name",
            "who are you",
            "tell me your name",
        ]

        if command in name_commands:
            response = "I am Jarvis, your personal artificial intelligence assistant."
            self.save_memory(command, response)
            return response

        # ==================================================
        # TIME
        # ==================================================
        if re.search(r"\btime\b", command):
            response = f"The current time is {self.current_time()}."
            self.save_memory(command, response)
            return response

        # ==================================================
        # DATE
        # ==================================================
        if re.search(r"\bdate\b", command) or re.search(r"\btoday\b", command):
            response = f"Today is {self.current_date()}."
            self.save_memory(command, response)
            return response

        # ==================================================
        # HELP
        # ==================================================
        help_commands = [
            "help",
            "commands",
            "show commands",
            "what can you do",
            "features",
            "capabilities",
        ]

        if command in HELP_COMMAND_SYNONYMS:
            self.print_help()
            response = "These are my available commands."
            self.save_memory(command, response)
            return response

        # ==================================================
        # EXIT
        # ==================================================
        exit_commands = ["exit", "quit", "shutdown", "goodbye", "bye"]

        if command in exit_commands:
            response = "Goodbye. Have a great day."
            self.save_memory(command, response)
            return response

        # ==================================================
        # UNKNOWN COMMAND SUGGESTIONS
        # ==================================================
        suggestions = {
            "dataset statics": "dataset statistics",
            "dataset statistic": "dataset statistics",
            "statistics dataset": "dataset statistics",
            "column": "columns",
            "samples": "sample tweets",
            "tweet": "sample tweets",
            "searching": "search <keyword>",
            "cleaning": "clean <text>",
            "token": "tokenize <text>",
            "name": "what is your name",
            "clock": "time",
            "today date": "date",
        }

        for wrong, correct in suggestions.items():
            if wrong in command:
                response = f"Did you mean '{correct}'?"
                self.save_memory(command, response)
                return response

        # ==================================================
        # TAUGHT KNOWLEDGE BASE (Training Mode)
        # ==================================================
        # Checked BEFORE the LLM fallback / default "I don't
        # understand" message — anything you taught in Training
        # Mode is used automatically here, without you needing
        # to mention Training Mode again.
        knowledge_response = knowledge_engine.answer_query(command)

        if knowledge_response is not None:
            self.save_memory(command, knowledge_response)
            return knowledge_response

        # ==================================================
        # OPEN-TOPIC FALLBACK (local LLM via Ollama)
        # ==================================================
        # Reached only if nothing above matched. Instead of a
        # canned "I don't understand", this sends the command to
        # a locally running Ollama model so Jarvis can talk about
        # anything, not just the built-in command list.
        if ENABLE_LLM_FALLBACK:
            import llm_engine
            response = llm_engine.ask_llm(command)
            self.save_memory(command, response)
            return response

        # ==================================================
        # DEFAULT RESPONSE (used only if the LLM fallback above
        # is turned off in config.py)
        # ==================================================
        response = (
            "Sorry, I don't understand that command yet. "
            "Type 'help' to see the available commands."
        )
        self.save_memory(command, response)
        return response


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":
    brain = JarvisBrain()

    print()
    print("=" * 60)
    print("JARVIS BRAIN TEST")
    print("=" * 60)
    print("Type 'exit' to close.")
    print("=" * 60)

    while True:
        query = input("\nYou : ").strip()

        reply = brain.get_response(query)

        print()
        print("Jarvis :", reply)

        if query.lower() in ["exit", "quit", "shutdown", "bye", "goodbye"]:
            break

    print()
    print("=" * 60)
    print("Brain Test Finished.")
    print("=" * 60)
