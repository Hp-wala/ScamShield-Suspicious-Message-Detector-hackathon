from pathlib import Path
from typing import Any, Dict, List, Optional


class LanguageManager:
    def __init__(self, supported_languages: Optional[List[str]] = None) -> None:
        self.supported_languages = supported_languages or ['en', 'hi', 'as', 'bn']
        self.default_language = 'en'

    def supported(self) -> List[str]:
        return list(self.supported_languages)

    def normalize_language(self, language: Optional[str]) -> str:
        if not language:
            return self.default_language
        language = language.lower().strip()
        return language if language in self.supported_languages else self.default_language

    def translate_response(self, response: Dict[str, Any], language: Optional[str] = None) -> Dict[str, Any]:
        language = self.normalize_language(language)
        if language == self.default_language:
            return response
        # Placeholder translation: keep text unchanged but annotate requested language.
        localized = dict(response)
        localized['language'] = language
        localized['translation_note'] = 'translation layer placeholder; content remains in source language.'
        return localized

    def localize_metadata(self, metadata: Dict[str, Any], language: Optional[str] = None) -> Dict[str, Any]:
        language = self.normalize_language(language)
        result = dict(metadata)
        result['language'] = language
        return result
