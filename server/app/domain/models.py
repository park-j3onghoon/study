"""Pure domain models. Frozen dataclasses (immutable value/entity objects).
Only stdlib imports + sibling exceptions module.
"""
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from .exceptions import InvalidConceptId, InvalidConversationId


_CONCEPT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")

QuestionType = Literal["multiple_choice", "short_answer"]


@dataclass(frozen=True)
class ConceptId:
    """URL-safe slug identifying a lesson. Validates on construction."""
    value: str

    def __post_init__(self) -> None:
        if not _CONCEPT_ID_RE.match(self.value):
            raise InvalidConceptId(self.value)


@dataclass(frozen=True)
class Question:
    id: str
    type: QuestionType
    prompt: str
    options: tuple[str, ...] | None = None
    correct: str | None = None
    expected_keywords: tuple[str, ...] | None = None


@dataclass(frozen=True)
class Lesson:
    concept_id: ConceptId
    title: str
    html: str
    questions: tuple[Question, ...]
    created: datetime
    model: str | None = None
    thinking_budget: int | None = None


@dataclass(frozen=True)
class Answers:
    concept_id: ConceptId
    submitted_at: datetime
    values: dict[str, str]


@dataclass(frozen=True)
class QuestionResult:
    question_id: str
    correct: bool
    comment: str = ""


@dataclass(frozen=True)
class Result:
    concept_id: ConceptId
    graded_at: datetime
    score: str
    by_question: tuple[QuestionResult, ...]
    weakness_tags: tuple[str, ...] = ()
    recommendation: str = ""


@dataclass(frozen=True)
class LessonSummary:
    """Sidebar용 view. Lesson 전체 대신 가벼운 요약 + 채점 여부."""
    concept_id: ConceptId
    title: str
    created: datetime
    graded: bool


@dataclass(frozen=True)
class ConversationId:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise InvalidConversationId(self.value)


def new_conversation_id() -> ConversationId:
    """Factory — domain-level uuid helper. Kept as module function (not classmethod)
    to keep ConversationId a pure value object."""
    return ConversationId(uuid.uuid4().hex)


@dataclass(frozen=True)
class Conversation:
    id: ConversationId
    title: str
    created: datetime
    messages: tuple[dict, ...]


@dataclass(frozen=True)
class ConversationSummary:
    id: ConversationId
    title: str
    created: datetime
    message_count: int
