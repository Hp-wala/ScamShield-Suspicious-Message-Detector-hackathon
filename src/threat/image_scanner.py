import os
import tempfile
from pathlib import Path


def validate_image_upload(file_storage):
    try:
        from PIL import Image
    except ImportError:
        return {"valid": False, "reason": "Pillow_not_installed"}
    try:
        if file_storage.content_length and file_storage.content_length > 5 * 1024 * 1024:
            return {"valid": False, "reason": "file_too_large"}
        image = Image.open(file_storage)
        image.verify()
        if image.format.lower() not in {"png", "jpeg", "jpg", "webp"}:
            return {"valid": False, "reason": "unsupported_format"}
        file_storage.seek(0)
        return {"valid": True, "format": image.format.lower()}
    except Exception:
        return {"valid": False, "reason": "invalid_image"}


def scan_qr(image_path):
    try:
        from pyzbar.pyzbar import decode
        from PIL import Image
    except ImportError:
        return {"status": "skipped", "reason": "pyzbar_or_pillow_not_installed", "urls": []}
    try:
        decoded = decode(Image.open(image_path))
        urls = [item.data.decode("utf-8", "replace") for item in decoded]
        return {"status": "ok", "urls": urls}
    except Exception as exc:
        return {"status": "skipped", "reason": "qr_decode_failed", "detail": str(exc)[:100], "urls": []}


def scan_ocr(image_path):
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return {"status": "skipped", "reason": "pytesseract_or_pillow_not_installed", "text": ""}
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return {"status": "ok", "text": text}
    except Exception as exc:
        return {"status": "skipped", "reason": "ocr_failed", "detail": str(exc)[:100], "text": ""}


def process_image(file_storage, engine):
    validation = validate_image_upload(file_storage)
    if not validation["valid"]:
        return {"status": "error", "reason": validation["reason"]}
    suffix = ".jpg" if validation["format"] == "jpeg" else "." + validation["format"]
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    try:
        file_storage.save(path)
        qr = scan_qr(path)
        ocr = scan_ocr(path)
        qr_results = []
        for url in qr["urls"]:
            qr_results.append(engine.analyze(url, "url"))
        ocr_result = engine.analyze(ocr["text"], "sms") if ocr["status"] == "ok" and ocr["text"].strip() else None
        return {
            "status": "ok",
            "format": validation["format"],
            "qr": qr,
            "qr_analysis": qr_results,
            "ocr": {"status": ocr["status"], "reason": ocr.get("reason")},
            "ocr_analysis": ocr_result,
        }
    finally:
        try:
            Path(path).unlink(missing_ok=True)
        except OSError:
            pass
