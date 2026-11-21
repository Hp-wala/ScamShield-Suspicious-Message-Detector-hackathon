# ==========================================================
# JARVIS AI
# CONFIGURATION FILE
# Python 3.12
# ==========================================================

import os

# ==========================================================
# PROJECT INFORMATION
# ==========================================================

PROJECT_NAME = "Jarvis AI"

VERSION = "1.0"

AUTHOR = "Ritul"


# ==========================================================
# KOKORO MODEL PATHS
# ==========================================================

MODEL_PATH = r"C:\AI\kokoro-v1.0.onnx"

VOICES_PATH = r"C:\AI\voices-v1.0.bin"


# ==========================================================
# DATASET PATH
# ==========================================================

DATASET_PATH = (
    r"C:\Users\ritul\OneDrive\Desktop\internship\twitter_training.csv"
)


# ==========================================================
# VOICE SETTINGS
# ==========================================================

VOICE = "af_sarah"

LANGUAGE = "en-us"

VOICE_SPEED = 1.0


# ==========================================================
# SPEECH RECOGNITION SETTINGS
# ==========================================================

MIC_LANGUAGE = "en-in"

LISTEN_TIMEOUT = 10

PHRASE_TIME_LIMIT = 5

AMBIENT_NOISE_DURATION = 1


# ==========================================================
# NLTK SETTINGS
# ==========================================================

NLTK_RESOURCES = [

    "punkt",

    "punkt_tab"

]


# ==========================================================
# LOCAL LLM FALLBACK (open-topic conversation via Ollama)
# ==========================================================
# When a command doesn't match any built-in rule, Jarvis will
# send it to a locally running Ollama model instead of just
# replying "I don't understand". This is free and fully offline.
#
# Requirements:
#   1. Ollama must be running in the background (it usually
#      starts automatically after installation on Windows).
#   2. OLLAMA_MODEL below must match a model you've pulled,
#      e.g. run `ollama list` in a terminal to check the exact
#      name/tag (yours was "qwen2.5-coder:3b").
#
# Set ENABLE_LLM_FALLBACK to False to go back to the old
# "Sorry, I don't understand" behaviour.

ENABLE_LLM_FALLBACK = False

OLLAMA_URL = "http://localhost:11434/api/generate"

OLLAMA_MODEL = "qwen2.5-coder:3b"

OLLAMA_TIMEOUT = 30

JARVIS_PERSONA = (
    "You are Jarvis, a helpful personal AI assistant built by Ritul. "
    "Answer clearly and concisely, in 2 to 4 sentences unless the user "
    "asks for more detail. Keep a friendly, direct tone."
)


# ==========================================================
# CHECK REQUIRED FILES
# ==========================================================

def verify_paths():

    print("Checking required files...\n")

    optional_files = [MODEL_PATH, VOICES_PATH, DATASET_PATH]

    for file_path in optional_files:
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

    missing_files = [path for path in optional_files if not os.path.exists(path)]

    if missing_files:
        print("Warning: optional files missing:\n")
        for file in missing_files:
            print(file)
        print("The application will continue with reduced capabilities.\n")
    else:
        print("All optional paths exist.\n")


# ==========================================================
# SHOW CONFIGURATION
# ==========================================================

def show_config():

    print("=" * 60)

    print("PROJECT CONFIGURATION")

    print("=" * 60)

    print(f"Project      : {PROJECT_NAME}")

    print(f"Version      : {VERSION}")

    print(f"Author       : {AUTHOR}")

    print()

    print("MODEL PATH")

    print(MODEL_PATH)

    print()

    print("VOICE PATH")

    print(VOICES_PATH)

    print()

    print("DATASET PATH")

    print(DATASET_PATH)

    print()

    print("VOICE")

    print(VOICE)

    print()

    print("LANGUAGE")

    print(LANGUAGE)

    print()

    print("=" * 60)