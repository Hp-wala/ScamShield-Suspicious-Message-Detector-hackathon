# ==========================================================
# JARVIS AI
# TRIGGERS ENGINE
# Python 3.12
# ==========================================================
#
# HOW THIS WORKS
# --------------
# 1. Each entry below has a key (trigger name), a list of
#    "match" phrases (what the user might say), and a list of
#    "responses" (what Jarvis can reply with).
#
# 2. When the user's command matches one of the "match"
#    phrases, Jarvis picks ONE response randomly from the
#    "responses" block — and won't repeat the same one twice
#    in a row for that trigger.
#
# 3. TO ADD YOUR OWN: just copy a block below, change the key,
#    add your match phrases, and add as many responses as you
#    want. No other code needs to change.
#
# Example:
#
#   "good_morning": {
#       "match": ["good morning", "gm", "morning jarvis"],
#       "responses": [
#           "Good morning! Ready to make today count?",
#           "Morning! Hope you slept well.",
#           "Good morning, Ritul. What's the plan today?",
#       ],
#   },
#
# ==========================================================

TRIGGERS = {

    # ------------------------------------------------------
    "good_morning": {
        "match": [
            "good morning",
            "gm",
            "morning jarvis",
        ],
        "responses": [
            "Good morning! Ready to make today count?",
            "Morning! Hope you slept well.",
            "Good morning, Ritul. What's on the agenda today?",
            "Rise and shine. Let's get to work.",
        ],
    },

    # ------------------------------------------------------
    "good_night": {
        "match": [
            "good night",
            "gn",
            "going to sleep",
            "night jarvis",
        ],
        "responses": [
            "Good night. Sleep well.",
            "Night, Ritul. Rest up, big day tomorrow.",
            "Good night. I'll be here when you wake up.",
        ],
    },

    # ------------------------------------------------------
    "how_are_you": {
        "match": [
            "how are you",
            "how are you doing",
            "are you fine",
            "how do you feel",
        ],
        "responses": [
            "I am functioning perfectly and ready to help you.",
            "All systems good on my end. How about you?",
            "Doing well, thanks for asking.",
        ],
    },

    # ------------------------------------------------------
    "thanks": {
        "match": [
            "thank you",
            "thanks",
            "thanks jarvis",
            "appreciate it",
        ],
        "responses": [
            "Anytime.",
            "You're welcome.",
            "Always happy to help.",
            "No problem at all.",
        ],
    },

    # ------------------------------------------------------
    "user_happy": {
        "match": [
            "i am happy",
            "i'm happy",
            "feeling great",
            "feeling good",
            "i am excited",
        ],
        "responses": [
            "That's great to hear!",
            "Love that energy. What's got you excited?",
            "Good moods are contagious, glad you're feeling this way.",
        ],
    },

    # ------------------------------------------------------
    "user_sad": {
        "match": [
            "i am sad",
            "i'm sad",
            "feeling down",
            "feeling low",
            "not feeling good",
        ],
        "responses": [
            "Sorry to hear that. Want to talk about it?",
            "That's tough. I'm here if you want to vent.",
            "Take it easy on yourself today.",
        ],
    },

    # ------------------------------------------------------
    "user_tired": {
        "match": [
            "i am tired",
            "i'm tired",
            "feeling exhausted",
            "so tired",
        ],
        "responses": [
            "Sounds like you need a break.",
            "Don't push too hard, rest is important too.",
            "Maybe step away for a few minutes?",
        ],
    },

    # ------------------------------------------------------
    "user_bored": {
        "match": [
            "i am bored",
            "i'm bored",
            "so bored",
            "nothing to do",
        ],
        "responses": [
            "Want me to suggest something to work on?",
            "Boredom is a good sign you need a new challenge.",
            "We could pick up one of your side projects right now.",
        ],
    },

    # ------------------------------------------------------
    "praise_jarvis": {
        "match": [
            "you are amazing",
            "you are the best",
            "good job jarvis",
            "well done",
        ],
        "responses": [
            "Thanks, glad I could help.",
            "Appreciate that.",
            "Just doing my job.",
        ],
    },
}


# ==========================================================
# INTERNAL STATE — tracks last response per trigger so the
# same line doesn't repeat back to back
# ==========================================================

_last_response = {}


# ==========================================================
# MATCH A COMMAND AGAINST ALL TRIGGERS
# ==========================================================
# Returns the trigger key if found, else None.

def find_trigger(command):
    command = command.lower().strip()

    for key, data in TRIGGERS.items():
        if command in data["match"]:
            return key

    return None


# ==========================================================
# GET A RESPONSE FOR A TRIGGER (random, no immediate repeat)
# ==========================================================

import random


def get_trigger_response(key):
    responses = TRIGGERS[key]["responses"]

    if len(responses) == 1:
        chosen = responses[0]
    else:
        choices = [r for r in responses if r != _last_response.get(key)]
        chosen = random.choice(choices)

    _last_response[key] = chosen
    return chosen


# ==========================================================
# ONE-CALL HELPER — use this from brain.py
# ==========================================================
# Returns a response string if the command matched a trigger,
# otherwise returns None (so brain.py can fall through to its
# other checks).

def check_triggers(command):
    key = find_trigger(command)

    if key is None:
        return None

    return get_trigger_response(key)