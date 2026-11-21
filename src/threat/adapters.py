import re
from dataclasses import dataclass
from typing import Protocol, Any
from email import policy
from email.parser import BytesParser, Parser
from html.parser import HTMLParser


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
        normalized = text.replace("\u202f", " ").replace("\xa0", " ").replace("\u200e", "")
        patterns = (
            r"^(\d{1,2}/\d{1,2}/\d{2,4},\s+\d{1,2}:\d{2}(?:\s?[ap]m)?)\s+-\s+([^:]+):\s*(.*)$",
            r"^\[(\d{1,2}/\d{1,2}/\d{4},\s+\d{1,2}:\d{2}:\d{2})\]\s+([^:]+):\s*(.*)$",
        )
        messages = []
        current = None
        for index, line in enumerate(normalized.splitlines(), 1):
            if re.search(r"Messages and calls are end-to-end encrypted|<Media omitted>|created this group|left$", line, re.I):
                continue
            match = next((re.match(pattern, line, re.I) for pattern in patterns if re.match(pattern, line, re.I)), None)
            if match:
                if current:
                    messages.append(current)
                current = {
                    "id": str(len(messages) + 1),
                    "channel": "whatsapp",
                    "sender": match.group(2).strip(),
                    "timestamp": match.group(1),
                    "text": match.group(3).strip(),
                    "meta": {"forwarded": "forwarded many times" in line.lower()},
                }
            elif current:
                current["text"] += "\n" + line.strip()
        if current:
            messages.append(current)
        if messages:
            return {"type": "chat", "messages": messages[:500], "meta": {"total": len(messages)}}
        return {"id": "1", "channel": "whatsapp", "sender": sender or "", "timestamp": "", "text": normalized, "meta": {}}


class EmailAdapter(BaseAdapter):
    def normalize(self, text: str) -> str:
        text = super().normalize(text)
        return re.sub(r"\b(reply\s*to|from|subject)\s*:", " ", text, flags=re.I)

    def extract(self, text: str, sender: str | None = None) -> dict[str, Any]:
        raw = text.encode("utf-8")
        if re.search(r"(?im)^([A-Z][A-Za-z0-9-]*):\s*", text):
            message = BytesParser(policy=policy.default).parsebytes(raw)
            subject = str(message.get("Subject", "") or "")
            from_header = str(message.get("From", "") or "")
            reply_to = str(message.get("Reply-To", "") or "")
            body_parts = []
            attachments = []
            if message.is_multipart():
                for part in message.walk():
                    disposition = part.get_content_disposition()
                    filename = part.get_filename()
                    if disposition == "attachment" or filename:
                        attachments.append(filename or "attachment")
                        continue
                    if part.get_content_type() == "text/plain":
                        body_parts.append(part.get_content())
                    elif part.get_content_type() == "text/html" and not body_parts:
                        body_parts.append(self._html_to_text(part.get_content()))
            else:
                body = message.get_payload(decode=True)
                body_parts.append(body.decode(message.get_content_charset() or "utf-8", "replace") if isinstance(body, bytes) else str(message.get_payload()))
            body = "\n".join(body_parts)
            return {
                "id": "1", "channel": "email", "sender": from_header, "timestamp": str(message.get("Date", "") or ""),
                "text": self.normalize(subject + "\n" + body),
                "meta": {"subject": subject, "from": from_header, "reply_to": reply_to, "attachments": attachments},
            }
        return {"id": "1", "channel": "email", "sender": sender or "", "timestamp": "", "text": self.normalize(text),
                "meta": {"subject": "", "from": sender or "", "reply_to": "", "attachments": []}}

    @staticmethod
    def _html_to_text(html: str) -> str:
        class TextParser(HTMLParser):
            def __init__(self) -> None:
                super().__init__()
                self.parts = []
            def handle_data(self, data: str) -> None:
                self.parts.append(data)
        parser = TextParser()
        parser.feed(html)
        return " ".join(parser.parts)


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
