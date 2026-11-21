import re
from dataclasses import dataclass
from typing import Protocol, Any


@dataclass
class Message:
    id: str
    channel: str
    sender: str
    timestamp: str
    text: str
    meta: dict[str, Any]


class ChannelAdapter(Protocol):
    def normalize(self, text: str) -> str: ...


class BaseAdapter:
    def validate(self, text: str) -> bool:
        return isinstance(text, str) and bool(text.strip()) and len(text) <= 5000

    def extract(self, text: str, sender: str | None = None) -> dict[str, Any]:
        return {"id": "1", "channel": "sms", "sender": sender or "", "timestamp": "", "text": self.normalize(text), "meta": {}}

    def normalize(self, text: str) -> str:
        text = text.strip()
        text = re.sub(r"<[^>]*>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text


class SmsAdapter(BaseAdapter):
    def extract(self, text: str, sender: str | None = None) -> dict[str, Any]:
        return {"id": "1", "channel": "sms", "sender": sender or "", "timestamp": "", "text": self.normalize(text), "meta": {}}


class WhatsappAdapter(BaseAdapter):
    def extract(self, text: str, sender: str | None = None) -> dict[str, Any]:
        return {"id": "1", "channel": "whatsapp", "sender": sender or "", "timestamp": "", "text": text.replace("\u202f", " ").replace("\xa0", " "), "meta": {}}


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


class AdapterRegistry:
    def __init__(self) -> None:
        self._adapters = dict(ADAPTERS)

    def register(self, channel: str, adapter: BaseAdapter) -> None:
        self._adapters[channel] = adapter

    def get(self, channel: str) -> BaseAdapter:
        return self._adapters.get(channel, SmsAdapter())


registry = AdapterRegistry()
