"""Domain ports — abstract contracts. Adapters layer fulfills these.

Method ordering follows the project convention (CRUD):
  save → find_* → list_* → exists.

CQS:
  Command methods return None (state change).
  Query methods return data (no side effect).
"""
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator

from .models import Answers, ConceptId, Lesson, LessonSummary, Result


class LessonRepository(ABC):
    """Persists lessons, answers, and results."""

    # Commands
    @abstractmethod
    def save(self, lesson: Lesson) -> None: ...

    @abstractmethod
    def save_answers(self, answers: Answers) -> None: ...

    @abstractmethod
    def save_result(self, result: Result) -> None: ...

    # Queries
    @abstractmethod
    def find_lesson(self, concept_id: ConceptId) -> Lesson | None: ...

    @abstractmethod
    def find_answers(self, concept_id: ConceptId) -> Answers | None: ...

    @abstractmethod
    def find_result(self, concept_id: ConceptId) -> Result | None: ...

    @abstractmethod
    def list_summaries(self) -> list[LessonSummary]: ...

    @abstractmethod
    def exists(self, concept_id: ConceptId) -> bool: ...


class Tool(ABC):
    """A capability the LLM agent can invoke. Concrete tools depend on application services."""
    name: str
    description: str
    input_schema: dict

    @abstractmethod
    async def execute(self, input: dict[str, Any]) -> str: ...


class Agent(ABC):
    """Streaming LLM agent. yields domain-level chat events."""

    @abstractmethod
    async def stream(
        self,
        messages: list[dict],
        model: str | None = None,
        thinking_budget: int | None = None,
    ) -> AsyncIterator[dict]: ...
