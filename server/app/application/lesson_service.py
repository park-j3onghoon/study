"""LessonService — use cases for lesson lifecycle.

CQS: Commands return None; Queries return data. Domain invariants live on the
models (e.g. Lesson.submit_answers); this service just enforces existence + delegates.
"""
from datetime import datetime, timezone

from ..domain.exceptions import LessonNotFound
from ..domain.models import ConceptId, Lesson, LessonSummary, Result
from ..domain.ports import LessonRepository


class LessonService:
    def __init__(self, repo: LessonRepository):
        self.repo = repo

    # ── Commands ────────────────────────────────────────────────────────────
    def create(self, lesson: Lesson) -> None:
        self.repo.save(lesson)

    def submit_answers(self, concept_id: ConceptId, values: dict[str, str]) -> None:
        lesson = self.repo.find_lesson(concept_id)
        if lesson is None:
            raise LessonNotFound(concept_id.value)
        answers = lesson.submit_answers(values, datetime.now(timezone.utc))
        self.repo.save_answers(answers)

    def save_result(self, result: Result) -> None:
        if not self.repo.exists(result.concept_id):
            raise LessonNotFound(result.concept_id.value)
        self.repo.save_result(result)

    # ── Queries ─────────────────────────────────────────────────────────────
    def list_summaries(self) -> list[LessonSummary]:
        return self.repo.list_summaries()

    def get(self, concept_id: ConceptId) -> Lesson:
        lesson = self.repo.find_lesson(concept_id)
        if lesson is None:
            raise LessonNotFound(concept_id.value)
        return lesson

    def find_answers(self, concept_id: ConceptId):
        return self.repo.find_answers(concept_id)

    def find_result(self, concept_id: ConceptId):
        return self.repo.find_result(concept_id)
