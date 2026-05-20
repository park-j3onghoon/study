"""Application service for lesson lifecycle.

CQS:
  Commands return None and change state via the repository.
  Queries return data and have no side effects.

This layer enforces domain policy (e.g. "cannot save answers for a non-existent lesson")
and converts between primitive inputs and domain objects when needed.
"""
from datetime import datetime, timezone

from ..domain.exceptions import LessonNotFound
from ..domain.models import Answers, ConceptId, Lesson, LessonSummary, Result
from ..domain.ports import LessonRepository


class LessonService:
    def __init__(self, repo: LessonRepository):
        self.repo = repo

    # ── Commands ────────────────────────────────────────────────────────────
    def create(self, lesson: Lesson) -> None:
        self.repo.save(lesson)

    def save_answers(self, concept_id: ConceptId, values: dict[str, str]) -> None:
        if not self.repo.exists(concept_id):
            raise LessonNotFound(concept_id.value)
        self.repo.save_answers(
            Answers(concept_id=concept_id, submitted_at=_now(), values=values)
        )

    def save_result(self, result: Result) -> None:
        if not self.repo.exists(result.concept_id):
            raise LessonNotFound(result.concept_id.value)
        self.repo.save_result(result)

    # ── Queries ─────────────────────────────────────────────────────────────
    def list_summaries(self) -> list[LessonSummary]:
        return self.repo.list_summaries()

    def get(self, concept_id: ConceptId) -> Lesson:
        """Retrieve by id. Raises LessonNotFound if absent (per project convention:
        'get' implies existence; use find_* for nullable lookups)."""
        lesson = self.repo.find_lesson(concept_id)
        if lesson is None:
            raise LessonNotFound(concept_id.value)
        return lesson

    def find_answers(self, concept_id: ConceptId) -> Answers | None:
        return self.repo.find_answers(concept_id)

    def find_result(self, concept_id: ConceptId) -> Result | None:
        return self.repo.find_result(concept_id)


def _now() -> datetime:
    return datetime.now(timezone.utc)
