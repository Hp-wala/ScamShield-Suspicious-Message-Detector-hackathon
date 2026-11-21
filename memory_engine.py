# ==========================================================
# JARVIS AI
# MEMORY ENGINE
# Python 3.12
# Version 1.0
# ==========================================================

import json
import os
import datetime


MEMORY_FILE = "memory.json"


# ==========================================================
# MEMORY ENGINE
# ==========================================================

class MemoryEngine:

    def __init__(self):
        self.memory = {
            "user": {},
            "history": [],
            "commands": {},
            "behaviour": {},
        }

        self.load_memory()

    # ======================================================
    # LOAD MEMORY
    # ======================================================

    def load_memory(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r") as file:
                    self.memory = json.load(file)
            except:
                self.save_memory()

    # ======================================================
    # SAVE MEMORY
    # ======================================================

    def save_memory(self):
        with open(MEMORY_FILE, "w") as file:
            json.dump(self.memory, file, indent=4)

    # ======================================================
    # STORE CHAT HISTORY
    # ======================================================

    def remember_chat(self, user_input, jarvis_reply):
        data = {
            "time": str(datetime.datetime.now()),
            "user": user_input,
            "jarvis": jarvis_reply,
        }

        self.memory["history"].append(data)

        # keep last 100 chats
        self.memory["history"] = self.memory["history"][-100:]

        self.save_memory()

    # ======================================================
    # TRACK COMMAND USAGE
    # ======================================================

    def track_command(self, command):
        if command in self.memory["commands"]:
            self.memory["commands"][command] += 1
        else:
            self.memory["commands"][command] = 1

        self.save_memory()

    # ======================================================
    # STORE USER PREFERENCE
    # ======================================================

    def remember_preference(self, key, value):
        self.memory["user"][key] = value
        self.save_memory()

    # ======================================================
    # GET USER PREFERENCE
    # ======================================================

    def get_preference(self, key):
        return self.memory["user"].get(key, None)

    # ======================================================
    # MOST USED COMMAND
    # ======================================================

    def most_used_command(self):
        commands = self.memory["commands"]

        if not commands:
            return None

        return max(commands, key=commands.get)

    # ======================================================
    # BEHAVIOUR ANALYSIS
    # ======================================================

    def analyse_behaviour(self):
        result = []

        commands = self.memory["commands"]

        if len(commands) == 0:
            return "I am still learning your usage pattern."

        # frequent command
        common = self.most_used_command()

        if common:
            result.append(f"You frequently use '{common}'.")

        # history size
        chats = len(self.memory["history"])

        result.append(f"We have interacted {chats} times.")

        return " ".join(result)

    # ======================================================
    # MEMORY SUMMARY
    # ======================================================

    def summary(self):
        return {
            "total_chats": len(self.memory["history"]),
            "commands": self.memory["commands"],
            "user": self.memory["user"],
        }