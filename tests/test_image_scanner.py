import io

from src.threat.image_scanner import validate_image_upload


class DummyUpload:
    content_length = 100

    def __init__(self, data):
        self.data = io.BytesIO(data)

    def seek(self, _offset):
        self.data.seek(0)

    def read(self, *args):
        return self.data.read(*args)


def test_invalid_image_rejected():
    upload = DummyUpload(b"not an image")
    assert validate_image_upload(upload)["valid"] is False
