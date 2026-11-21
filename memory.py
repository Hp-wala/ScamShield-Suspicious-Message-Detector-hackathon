# ==========================================================
# JARVIS AI
# MEMORY ENGINE
# Python 3.12
# Version 3.0
# ==========================================================

import datetime
import json
import os
import re


# ==========================================================
# STORAGE LOCATIONS
# ==========================================================

MEMORY_DIR = "memory_data"
CONVERSATION_FILE = os.path.join(MEMORY_DIR, "conversation.json")
PROFILE_FILE = os.path.join(MEMORY_DIR, "profile.json")

# words ignored when detecting "topics" the user talks about
STOPWORDS = {
    "the", "is", "a", "an", "and", "to", "of", "in", "on", "for",
    "my", "your", "i", "you", "me", "what", "do", "know", "about",
    "are", "am", "it", "this", "that", "was", "were", "be", "can",
    "will", "with", "have", "has", "does",
}

# simple keyword map used for mood detection
MOOD_KEYWORDS = {
    "tired": ["tired", "exhausted", "sleepy", "drained"],
    "happy": ["happy", "great", "excited", "awesome", "good mood"],
    "sad": ["sad", "down", "upset", "unhappy"],
    "stressed": ["stressed", "anxious", "overwhelmed", "worried"],
    "busy": ["busy", "swamped", "loaded with work"],
}


# ==========================================================
# JARVIS MEMORY CLASS
# ==========================================================

class JarvisMemory:

    # ======================================================
    # INITIALIZE MEMORY
    # ======================================================

    def __init__(self):
        self.history = []

        self.user_profile = {
            "name": None,
            "interests": [],
            "projects": [],
            "facts": {},
            "common_commands": {},
            "topics": {},
            "mood": None,
            "preferences": {
                "explanation_style": "simple",
            },
            "project": {},
        }

        self.created_time = datetime.datetime.now()

        self._ensure_storage()
        self.load_memory()

    # ======================================================
    # STORAGE SETUP
    # ======================================================

    def _ensure_storage(self):
        os.makedirs(MEMORY_DIR, exist_ok=True)

    # ======================================================
    # LOAD MEMORY FROM DISK
    # ======================================================

    def load_memory(self):
        if os.path.exists(CONVERSATION_FILE):
            try:
                with open(CONVERSATION_FILE, "r") as file:
                    self.history = json.load(file)
            except Exception:
                self.history = []

        if os.path.exists(PROFILE_FILE):
            try:
                with open(PROFILE_FILE, "r") as file:
                    saved_profile = json.load(file)
                    self.user_profile.update(saved_profile)
            except Exception:
                pass

    # ======================================================
    # SAVE MEMORY TO DISK
    # ======================================================

    def save_conversation(self):
        try:
            with open(CONVERSATION_FILE, "w") as file:
                json.dump(self.history[-200:], file, indent=4)
        except Exception as error:
            print(f"[Memory Warning] Could not save conversation: {error}")

    def save_profile(self):
        try:
            with open(PROFILE_FILE, "w") as file:
                json.dump(self.user_profile, file, indent=4)
        except Exception as error:
            print(f"[Memory Warning] Could not save profile: {error}")

    # ======================================================
    # STORE CONVERSATION
    # ======================================================

    def remember(self, user_message, jarvis_response):
        conversation = {
            "time": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "user": user_message,
            "jarvis": jarvis_response,
        }

        self.history.append(conversation)
        self.history = self.history[-200:]

        self.update_patterns(user_message)
        self.save_conversation()

    # ======================================================
    # ALIAS FOR EXTERNAL CALLERS (e.g. main.py)
    # ======================================================

    def remember_chat(self, user_message, jarvis_response):
        self.remember(user_message, jarvis_response)

    # ======================================================
    # LEARN USER PATTERN (commands + topics)
    # ======================================================

    def update_patterns(self, command):
        command = command.lower()

        commands = self.user_profile["common_commands"]
        commands[command] = commands.get(command, 0) + 1

        topics = self.user_profile["topics"]

        for word in command.split():
            word = re.sub(r"[^a-z0-9]", "", word)

            if len(word) < 4 or word in STOPWORDS:
                continue

            topics[word] = topics.get(word, 0) + 1

        self.save_profile()

    # ======================================================
    # FACTS MEMORY (remember / recall / forget)
    # ======================================================

    def remember_fact(self, key, value):
        key = key.strip().lower()
        value = value.strip()

        self.user_profile["facts"][key] = value
        self.save_profile()

        return f"Got it. I'll remember that your {key} is {value}."

    def get_fact(self, key):
        key = key.strip().lower()
        return self.user_profile["facts"].get(key)

    def forget_fact(self, key):
        key = key.strip().lower()

        if key in self.user_profile["facts"]:
            del self.user_profile["facts"][key]
            self.save_profile()
            return f"Okay, I've forgotten your {key}."

        return f"I didn't have anything saved about your {key}."

    def list_facts(self):
        return self.user_profile["facts"]

    # ======================================================
    # PROJECT MEMORY (structured, separate from generic facts)
    # ======================================================

    def remember_project(self, key, value):
        key = key.strip().lower()
        value = value.strip()

        self.user_profile.setdefault("project", {})
        self.user_profile["project"][key] = value
        self.save_profile()

        return f"Got it. I'll remember that your project's {key} is {value}."

    def get_project_info(self, key):
        key = key.strip().lower()
        return self.user_profile.get("project", {}).get(key)

    def project_summary(self):
        project = self.user_profile.get("project", {})

        if not project:
            return "I don't know anything about this project yet."

        parts = [f"{key}: {value}" for key, value in project.items()]

        return "Your project details -> " + ", ".join(parts) + "."

    # ======================================================
    # PROFILE (name / interests / projects list)
    # ======================================================

    def save_name(self, name):
        self.user_profile["name"] = name
        self.save_profile()

        return f"I will remember your name as {name}."

    def get_name(self):
        name = self.user_profile["name"]

        if name:
            return name

        return "I don't know your name yet."

    def add_interest(self, interest):
        interest = interest.strip()

        if interest and interest not in self.user_profile["interests"]:
            self.user_profile["interests"].append(interest)
            self.save_profile()

    def add_project(self, project):
        project = project.strip()

        if project and project not in self.user_profile["projects"]:
            self.user_profile["projects"].append(project)
            self.save_profile()

    # ======================================================
    # PREFERENCE MEMORY
    # ======================================================

    def set_preference(self, key, value):
        self.user_profile.setdefault("preferences", {})
        self.user_profile["preferences"][key] = value
        self.save_profile()

    def get_preference(self, key, default=None):
        return self.user_profile.get("preferences", {}).get(key, default)

    # ======================================================
    # MOOD DETECTION MEMORY
    # ======================================================

    def detect_mood(self, command):
        command = command.lower()

        for mood, keywords in MOOD_KEYWORDS.items():
            for keyword in keywords:
                if keyword in command:
                    self.user_profile["mood"] = mood
                    self.save_profile()
                    return mood

        return None

    def get_mood(self):
        return self.user_profile.get("mood")

    # ======================================================
    # MEMORY SUMMARY
    # ======================================================

    def summary(self):
        total = len(self.history)

        if total == 0:
            return "My memory is empty. I have not learned anything yet."

        last_chat = self.history[-1]

        return {
            "Total Conversations": total,
            "Memory Created": self.created_time.strftime("%d %B %Y"),
            "Last User Message": last_chat["user"],
            "Last Jarvis Response": last_chat["jarvis"],
            "Known Facts": self.user_profile["facts"],
            "Project": self.user_profile.get("project", {}),
        }

    # ======================================================
    # BEHAVIOUR ANALYSIS
    # ======================================================

    def analyse_behaviour(self):
        if len(self.history) == 0:
            return "I need more conversations before analysing your behaviour."

        commands = self.user_profile["common_commands"]
        most_used = max(commands, key=commands.get)
        count = commands[most_used]
        total = len(self.history)

        topics = self.user_profile["topics"]
        top_topics = sorted(
            topics.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:3]

        if top_topics:
            topic_line = ", ".join(topic for topic, _ in top_topics)
        else:
            topic_line = "nothing specific yet"

        facts_line = ""

        if self.user_profile["facts"]:
            known = ", ".join(
                f"{key}: {value}"
                for key, value in self.user_profile["facts"].items()
            )
            facts_line = f"\n\nThings I know about you: {known}."

        mood = self.get_mood()
        mood_line = f"\n\nYour most recent mood seemed to be: {mood}." if mood else ""

        analysis = (
            f"Behaviour Analysis:\n\n"
            f"You have interacted with me {total} times.\n\n"
            f"Your most frequently used command is '{most_used}' "
            f"({count} times).\n\n"
            f"You often talk about: {topic_line}.\n\n"
            f"You prefer direct command based interaction with Jarvis."
            f"{facts_line}"
            f"{mood_line}"
        )

        return analysis

    # ======================================================
    # MEMORY SEARCH
    # ======================================================

    def search_memory(self, keyword):
        keyword = keyword.lower().strip()

        if not keyword:
            return []

        matches = [
            entry for entry in self.history
            if keyword in entry["user"].lower()
            or keyword in entry["jarvis"].lower()
        ]

        return matches

    # ======================================================
    # MEMORY TIMELINE
    # ======================================================

    def timeline(self):
        grouped = {}

        for entry in self.history:
            date_part, time_part = entry["time"].split(" ")
            grouped.setdefault(date_part, []).append(
                (time_part, entry["user"], entry["jarvis"])
            )

        return grouped

    # ======================================================
    # GET RECENT MEMORY
    # ======================================================

    def recent_memory(self, limit=5):
        if len(self.history) == 0:
            return "No previous conversations found."

        return self.history[-limit:]

    # ======================================================
    # CLEAR MEMORY
    # ======================================================

    def clear_memory(self):
        self.history = []

        self.user_profile = {
            "name": None,
            "interests": [],
            "projects": [],
            "facts": {},
            "common_commands": {},
            "topics": {},
            "mood": None,
            "preferences": {
                "explanation_style": "simple",
            },
            "project": {},
        }

        self.save_conversation()
        self.save_profile()

        return "Memory cleared successfully."