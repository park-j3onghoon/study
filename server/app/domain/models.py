"""Pure domain models. Frozen dataclasses with invariants enforced in __post_init__.
Only stdlib + sibling exceptions module — no framework imports.
"""
import re
import uuid
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Literal

from .exceptions import InvalidConceptId, InvalidConversationId, InvalidQuestion


_CONCEPT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
# uuid4().hex → 32 lowercase hex chars. Blocks path traversal and arbitrary input.
_CONVERSATION_ID_RE = re.compile(r"^[0-9a-f]{32}$")

QuestionType = Literal["multiple_choice", "short_answer"]
_VALID_QUESTION_TYPES: frozenset[str] = frozenset({"multiple_choice", "short_answer"})


@dataclass(frozen=True)
class ConceptId:
    """URL-safe slug. Lowercase, digits, hyphens. Must start with [a-z0-9]."""
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

    def __post_init__(self) -> None:
        if self.type not in _VALID_QUESTION_TYPES:
            raise InvalidQuestion(f"invalid type: {self.type!r}")
        if not self.id:
            raise InvalidQuestion("id must be non-empty")
        if not self.prompt:
            raise InvalidQuestion("prompt must be non-empty")
        if self.type == "multiple_choice":
            if not self.options or len(self.options) < 2:
                raise InvalidQuestion("multiple_choice requires >= 2 options")
            if self.correct is not None and self.correct not in self.options:
                raise InvalidQuestion(
                    f"correct {self.correct!r} must be one of options {list(self.options)}"
                )


@dataclass(frozen=True)
class Lesson:
    concept_id: ConceptId
    title: str
    html: str
    questions: tuple[Question, ...]
    created: datetime
    model: str | None = None
    thinking_budget: int | None = None

    def submit_answers(self, values: dict[str, str], at: datetime) -> "Answers":
        """Domain operation: derive an Answers aggregate from raw user input.
        Lives on Lesson because the lesson dictates which question ids are valid."""
        question_ids = {q.id for q in self.questions}
        filtered = {qid: v for qid, v in values.items() if qid in question_ids}
        return Answers(concept_id=self.concept_id, submitted_at=at, values=filtered)


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

    def total_correct(self) -> int:
        return sum(1 for qr in self.by_question if qr.correct)

    def total(self) -> int:
        return len(self.by_question)

    def accuracy(self) -> float:
        """0.0 ~ 1.0. Empty by_question → 0.0 (no questions graded)."""
        if not self.by_question:
            return 0.0
        return self.total_correct() / self.total()


@dataclass(frozen=True)
class LessonSummary:
    """Sidebar view. Lighter than Lesson + 채점 여부 flag."""
    concept_id: ConceptId
    title: str
    created: datetime
    graded: bool


@dataclass(frozen=True)
class ConversationId:
    value: str

    def __post_init__(self) -> None:
        if not _CONVERSATION_ID_RE.match(self.value):
            raise InvalidConversationId(self.value)


def new_conversation_id() -> ConversationId:
    return ConversationId(uuid.uuid4().hex)


@dataclass(frozen=True)
class Conversation:
    id: ConversationId
    title: str
    created: datetime
    messages: tuple[dict, ...]

    def add_turn(self, user_content: str, assistant_content: str) -> "Conversation":
        """Append a user→assistant turn. Either side may be empty (skipped)."""
        new_msgs: list[dict] = []
        if user_content:
            new_msgs.append({"role": "user", "content": user_content})
        if assistant_content:
            new_msgs.append({"role": "assistant", "content": assistant_content})
        if not new_msgs:
            return self
        return replace(self, messages=self.messages + tuple(new_msgs))


@dataclass(frozen=True)
class ConversationSummary:
    id: ConversationId
    title: str
    created: datetime
    message_count: int


@dataclass(frozen=True)
class ModelInfo:
    """A model available to the agent. Provider-agnostic value object.
    `family` is set by the adapter (e.g. "opus"/"sonnet"/"haiku"/"other") so the
    domain can rank without knowing Anthropic naming."""
    id: str
    display_name: str
    family: str
    created_at: datetime


