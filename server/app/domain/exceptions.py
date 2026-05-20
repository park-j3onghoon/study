"""Domain-level exceptions. No imports from other layers."""


class DomainException(Exception):
    """Base for all domain exceptions."""


class InvalidConceptId(DomainException):
    def __init__(self, value: str):
        super().__init__(f"Invalid concept_id: {value!r}")
        self.value = value


class LessonNotFound(DomainException):
    def __init__(self, value: str):
        super().__init__(f"Lesson not found: {value!r}")
        self.value = value
