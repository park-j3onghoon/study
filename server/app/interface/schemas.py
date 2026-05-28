"""HTTP DTOs (pydantic). Adapt between FastAPI request/response and domain objects."""
from pydantic import BaseModel


class ChatRequest(BaseModel):
    messages: list[dict]
    model: str | None = None
    thinking_budget: int | None = None
    conversation_id: str | None = None


class ConversationCreateRequest(BaseModel):
    title: str


class ConversationSummaryDTO(BaseModel):
    id: str
    title: str
    created: str
    message_count: int


class ConversationDetailDTO(BaseModel):
    id: str
    title: str
    created: str
    messages: list[dict]


class AnswersPayload(BaseModel):
    answers: dict[str, str]


class LessonSummaryDTO(BaseModel):
    concept_id: str
    title: str
    created: str
    graded: bool


class QuestionDTO(BaseModel):
    id: str
    type: str
    prompt: str
    options: list[str] | None = None
    correct: str | None = None
    expected_keywords: list[str] | None = None


class LessonDTO(BaseModel):
    concept_id: str
    title: str
    created: str
    model: str | None = None
    thinking_budget: int | None = None
    questions: list[QuestionDTO]
    lesson_html: str


class QuestionResultDTO(BaseModel):
    id: str
    correct: bool
    comment: str = ""


class ResultDTO(BaseModel):
    graded_at: str
    score: str
    by_question: list[QuestionResultDTO]
    weakness_tags: list[str] = []
    recommendation: str = ""


class ModelDTO(BaseModel):
    id: str
    display_name: str
    family: str
    created_at: str
