import re
from typing import Protocol


class ChannelAdapter(Protocol):
    def normalize(self, text: str) -> str: ...


class BaseAdapter:
    def normalize(self, text: str) -> str:
        text = text.strip()
        text = re.sub(r"<[^>]*>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text


class SmsAdapter(BaseAdapter):
    pass


class WhatsappAdapter(BaseAdapter):
    pass


class EmailAdapter(BaseAdapter):
    def normalize(self, text: str) -> str:
        text = super().normalize(text)
        return re.sub(r"\b(reply\s*to|from|subject)\s*:", " ", text, flags=re.I)


class UrlAdapter(BaseAdapter):
    def normalize(self, text: str) -> str:
        urls = re.findall(r"https?://[^\s]+|www\.[^\s]+", text, re.I)
        return " ".join(urls) if urls else text.strip()


ADAPTERS = {
    "sms": SmsAdapter(),
    "whatsapp": WhatsappAdapter(),
    "email": EmailAdapter(),
    "url": UrlAdapter(),
}
