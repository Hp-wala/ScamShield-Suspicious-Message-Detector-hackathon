from typing import Dict, List


class Ontology:
    def __init__(self) -> None:
        self.subject_fields: Dict[str, List[str]] = {}

    def register_subject_fields(self, subject: str, fields: List[str]) -> None:
        self.subject_fields[subject] = fields

    def get_subject_fields(self, subject: str) -> List[str]:
        return self.subject_fields.get(subject, [])

    def is_supported_subject(self, subject: str) -> bool:
        return subject in self.subject_fields
