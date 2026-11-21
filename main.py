# ==========================================================
# JARVIS AI
# MAIN PROGRAM
# Python 3.12
# Version 2.0
# ==========================================================

import datetime
import traceback

from config import (
    verify_paths,
    show_config,
)

from src.inference.spam_service import SpamService
from tts_engine import (
    initialize_tts,
    speak,
)

from speech_engine import (
    initialize_microphone,
    take_command,
)

from brain import (
    JarvisBrain,
)


# ==========================================================
# GLOBAL OBJECT
# ==========================================================

brain = None
spam_service = None


# ==========================================================
# STARTUP BANNER
# ==========================================================

def startup_banner():
    print()
    print("=" * 60)
    print("              JARVIS AI")
    print("=" * 60)
    print()


# ==========================================================
# WISH USER
# ==========================================================

def wish():
    hour = datetime.datetime.now().hour

    if hour < 12:
        greeting = "Good morning."
    elif hour < 18:
        greeting = "Good afternoon."
    else:
        greeting = "Good evening."

    speak(greeting)
    speak("I am mridusa. Your personal artificial intelligence assistant.")
    speak("Please choose how you would like to interact with me.")


# ==========================================================
# INITIALIZE
# ==========================================================

def initialize():
    global brain, spam_service

    startup_banner()

    verify_paths()
    show_config()

    initialize_tts()
    initialize_microphone()

    brain = JarvisBrain()
    spam_service = SpamService()
    spam_service.load_model()

    print()
    print("=" * 60)
    print("Jarvis Initialization Complete.")
    print("=" * 60)
    print()


# ==========================================================
# SAVE MEMORY
# ==========================================================

def save_memory(user_input, response):
    try:
        brain.memory.remember_chat(user_input, response)
    except Exception:
        pass


# ==========================================================
# VOICE MODE
# ==========================================================

def voice_mode():
    global brain

    wish()

    while True:
        command = take_command()

        if command == "":
            continue

        response = brain.get_response(command)

        # SAVE CONVERSATION MEMORY
        save_memory(command, response)

        speak(response)

        if command.lower() in ["exit", "quit", "shutdown", "goodbye", "bye"]:
            print("\nVoice Mode Closed.")
            break


# ==========================================================
# CHAT MODE
# ==========================================================

def chat_mode():
    global brain

    print()
    print("=" * 60)
    print("CHAT MODE")
    print("=" * 60)
    print("Type 'exit' anytime to close Jarvis.")

    while True:
        query = input("\nYou : ").strip()

        if query == "":
            continue

        response = brain.get_response(query)

        # SAVE CONVERSATION MEMORY
        save_memory(query, response)

        print()
        print(f"Jarvis : {response}")

        if query.lower() in ["exit", "quit", "shutdown", "goodbye", "bye"]:
            break


# ==========================================================
# TRAINING MODE (dedicated menu option — no need to type
# "training mode" inside chat first)
# ==========================================================

def training_mode_cli():
    global brain

    print()
    print("=" * 60)
    print("TRAINING MODE")
    print("=" * 60)
    print("Teach Jarvis new facts, definitions, or code.")
    print("Type EXIT at any point to leave and return to the menu.")

    # Start the guided category -> subcategory -> teach flow
    response = brain.training.start()
    print()
    print(f"Jarvis : {response}")

    while True:
        query = input("\nYou : ").strip()

        if query == "":
            continue

        # Preserve original capitalization (important for code
        # and proper nouns) — do NOT lowercase this input.
        response = brain.training.handle_input(query)

        save_memory(query, response)

        print()
        print(f"Jarvis : {response}")

        if not brain.training.is_active():
            print("\nBack to the main menu next time you run Jarvis.")
            break


# ==========================================================
# SELECT MODE
# ==========================================================

def spam_email_detector():
    global spam_service

    print()
    print("=" * 60)
    print("SPAM EMAIL DETECTOR")
    print("=" * 60)
    print("Enter the email subject and body. Jarvis will evaluate whether it is likely spam.")
    print()

    subject = input("Subject: ").strip()
    body = input("Body: ").strip()

    if not subject and not body:
        print("No email content entered.")
        return

    email_data = {
        'subject': subject,
        'body': body,
        'from': '',
        'to': '',
        'reply_to': '',
        'headers': '',
    }

    label = 'ham'
    score = 0.0
    reasons = []

    if spam_service is not None:
        label = spam_service.predict(email_data)
        score = spam_service.predict_proba(email_data)
    else:
        label = 'ham'

    print()
    print("Result:", "Likely spam email." if label == 'spam' else "Probably not spam.")
    print(f"Spam score: {score:.2f}")

    feedback = input("Was this prediction correct? (yes/no): ").strip().lower()
    if feedback in {'yes', 'no'}:
        correct_label = label if feedback == 'yes' else ('ham' if label == 'spam' else 'spam')
        if spam_service is not None:
            saved = spam_service.submit_feedback(email_data, correct_label)
            print("Feedback saved." if saved else "Failed to save feedback.")
    else:
        print("Feedback skipped.")


def select_mode():
    print()
    print("=" * 60)
    print("SELECT INTERACTION MODE")
    print("=" * 60)
    print("1. Voice Mode")
    print("2. Chat Mode")
    print("3. Spam Email Detector")
    print("4. Training Mode")
    print()

    while True:
        choice = input("Enter choice (1, 2, 3 or 4): ").strip()

        if choice == "1":
            return "voice"
        elif choice == "2":
            return "chat"
        elif choice == "3":
            return "spam"
        elif choice == "4":
            return "training"
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")


# ==========================================================
# RUN JARVIS
# ==========================================================

def run():
    mode = select_mode()

    if mode == "voice":
        voice_mode()
    elif mode == "chat":
        chat_mode()
    elif mode == "spam":
        spam_email_detector()
    elif mode == "training":
        training_mode_cli()


# ==========================================================
# MAIN FUNCTION
# ==========================================================

def main():
    try:
        initialize()
        run()

    except FileNotFoundError as e:
        print()
        print("=" * 60)
        print("FILE ERROR")
        print("=" * 60)
        print(e)

    except KeyboardInterrupt:
        print()
        print("=" * 60)
        print("PROGRAM TERMINATED BY USER")
        print("=" * 60)

        try:
            speak("Goodbye.")
        except Exception:
            pass

    except Exception as e:
        print()
        print("=" * 60)
        print("UNEXPECTED ERROR")
        print("=" * 60)
        print(e)

        traceback.print_exc()

        try:
            speak("Sorry. An unexpected error occurred.")
        except Exception:
            pass

    finally:
        print()
        print("=" * 60)
        print("JARVIS CLOSED")
        print("=" * 60)


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()
