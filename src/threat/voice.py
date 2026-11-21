import os
import tempfile
from pathlib import Path


def analyze_transcript(text, engine):
    if not isinstance(text, str) or not text.strip():
        return {"status": "error", "reason": "Transcript is required"}
    result = engine.analyze(text, "sms")
    result.pop("text", None)
    result.pop("text_hash", None)
    return {"status": "ok", "analysis": result}


def analyze_audio(file_storage, engine):
    try:
        import vosk
    except ImportError:
        return {"status": "skipped", "reason": "vosk_not_installed"}
    model_path = os.getenv("VOSK_MODEL_PATH")
    if not model_path or not Path(model_path).is_dir():
        return {"status": "skipped", "reason": "VOSK_MODEL_PATH_not_configured"}
    suffix = Path(file_storage.filename or "").suffix.lower() or ".wav"
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    try:
        file_storage.save(path)
        try:
            import wave
            with wave.open(path, "rb") as audio:
                # Vosk integration intentionally depends on a locally downloaded model.
                return {
                    "status": "skipped",
                    "reason": "audio_transcription_requires_vosk_model_and_wav_decoding",
                }
        except (wave.Error, OSError):
            return {"status": "skipped", "reason": "audio_must_be_wav"}
    finally:
        try:
            Path(path).unlink(missing_ok=True)
        except OSError:
            pass
