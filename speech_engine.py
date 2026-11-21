# ==========================================================
# JARVIS AI
# SPEECH RECOGNITION ENGINE
# Python 3.12
# ==========================================================

import speech_recognition as sr

from config import (
    MIC_LANGUAGE,
    LISTEN_TIMEOUT,
    PHRASE_TIME_LIMIT,
    AMBIENT_NOISE_DURATION
)

# ==========================================================
# CREATE RECOGNIZER
# ==========================================================

recognizer = sr.Recognizer()

# ==========================================================
# INITIALIZE MICROPHONE
# ==========================================================

def initialize_microphone():

    print("=" * 60)
    print("Initializing Microphone...")
    print("=" * 60)

    try:

        with sr.Microphone() as source:

            recognizer.adjust_for_ambient_noise(
                source,
                duration=AMBIENT_NOISE_DURATION
            )

        print("Microphone Ready.")
        print("=" * 60)

    except Exception as e:

        print(f"Microphone Error : {e}")

# ==========================================================
# LISTEN
# ==========================================================

def listen():

    with sr.Microphone() as source:

        print("\nListening...")

        recognizer.adjust_for_ambient_noise(
            source,
            duration=AMBIENT_NOISE_DURATION
        )

        try:

            audio = recognizer.listen(

                source,

                timeout=LISTEN_TIMEOUT,

                phrase_time_limit=PHRASE_TIME_LIMIT

            )

            return audio

        except sr.WaitTimeoutError:

            print("No speech detected.")

            return None

# ==========================================================
# SPEECH TO TEXT
# ==========================================================

def speech_to_text(audio):

    if audio is None:

        return ""

    print("Recognizing...")

    try:

        text = recognizer.recognize_google(

            audio,

            language=MIC_LANGUAGE

        )

        text = text.lower()

        print(f"You : {text}")

        return text

    except sr.UnknownValueError:

        print("Could not understand audio.")

        return ""

    except sr.RequestError:

        print("Speech Recognition Service Unavailable.")

        return ""

    except Exception as e:

        print(f"Error : {e}")

        return ""

# ==========================================================
# COMPLETE COMMAND
# ==========================================================

def take_command():

    audio = listen()

    command = speech_to_text(audio)

    return command

# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    initialize_microphone()

    while True:

        command = take_command()

        if command == "":

            continue

        if "exit" in command:

            break

        print(command)