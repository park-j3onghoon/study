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


class InvalidParent(DomainException):
    """parent_id violates a hierarchy invariant (self-parent / cycle / dangling)."""

    def __init__(self, message: str):
        super().__init__(message)


class InvalidConversationId(DomainException):
    def __init__(self, value: str):
        super().__init__(f"Invalid conversation_id: {value!r}")
        self.value = value


class ConversationNotFound(DomainException):
    def __init__(self, value: str):
        super().__init__(f"Conversation not found: {value!r}")
        self.value = value


class InvalidSessionId(DomainException):
    def __init__(self, value: str):
        super().__init__(f"Invalid session_id: {value!r}")
        self.value = value


class InvalidQuestion(DomainException):
    """Invariant violation on Question construction."""
