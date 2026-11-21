# ==========================================================
# JARVIS AI
# TEXT TO SPEECH ENGINE
# Python 3.12
# ==========================================================

from kokoro_onnx import Kokoro
import sounddevice as sd

from config import (
    MODEL_PATH,
    VOICES_PATH,
    VOICE,
    LANGUAGE,
    VOICE_SPEED,
)

# ==========================================================
# GLOBAL VARIABLES
# ==========================================================

kokoro = None


# ==========================================================
# LOAD VOICE ENGINE
# ==========================================================

def initialize_tts():

    global kokoro

    if kokoro is not None:
        return

    print("=" * 60)
    print("Loading Jarvis Voice Engine...")
    print("=" * 60)

    kokoro = Kokoro(
        MODEL_PATH,
        VOICES_PATH
    )

    print("Voice Engine Loaded Successfully.")
    print("=" * 60)


# ==========================================================
# TEXT TO SPEECH
# ==========================================================

def speak(text):

    global kokoro

    if kokoro is None:

        initialize_tts()

    text = str(text)

    print(f"\nJarvis : {text}")

    audio, sample_rate = kokoro.create(

        text=text,

        voice=VOICE,

        speed=VOICE_SPEED,

        lang=LANGUAGE

    )

    sd.play(

        audio,

        sample_rate

    )

    sd.wait()


# ==========================================================
# STOP SPEAKING
# ==========================================================

def stop_speaking():

    try:

        sd.stop()

    except Exception:

        pass


# ==========================================================
# TEST VOICE
# ==========================================================

def test_voice():

    initialize_tts()

    speak(
        "Hello. I am Jarvis. My voice engine is working perfectly."
    )


# ==========================================================
# CHANGE VOICE
# ==========================================================

def change_voice(voice_name):

    global VOICE

    VOICE = voice_name


# ==========================================================
# CHANGE SPEED
# ==========================================================

def change_speed(speed):

    global VOICE_SPEED

    VOICE_SPEED = speed


# ==========================================================
# SPEAK MULTIPLE SENTENCES
# ==========================================================

def speak_list(sentences):

    for sentence in sentences:

        speak(sentence)


# ==========================================================
# MAIN TEST
# ==========================================================

if __name__ == "__main__":

    initialize_tts()

    test_voice()