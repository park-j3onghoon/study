"""LessonService — use cases for lesson lifecycle.

CQS: Commands return None; Queries return data. Domain invariants live on the
models (e.g. Lesson.submit_answers); this service just enforces existence + delegates.
"""
from datetime import datetime, timezone

from ..domain.exceptions import InvalidParent, LessonNotFound
from ..domain.models import ConceptId, Lesson, LessonSummary, Result
from ..domain.ports import LessonRepository


class LessonService:
    def __init__(self, repo: LessonRepository):
        self.repo = repo

    # ── Commands ────────────────────────────────────────────────────────────
    def create(self, lesson: Lesson) -> None:
        if lesson.parent_id is not None:
            if not self.repo.exists(lesson.parent_id):
                raise InvalidParent(f"parent {lesson.parent_id.value!r} does not exist")
            self._assert_no_cycle(lesson.concept_id, lesson.parent_id)
        if self.repo.exists(lesson.concept_id) and self.repo.find_result(lesson.concept_id) is not None:
            self.repo.archive_version(lesson.concept_id)
        self.repo.save(lesson)

    def _assert_no_cycle(self, concept_id: ConceptId, parent_id: ConceptId) -> None:
        # Walk parent links upward; a cycle exists if we reach concept_id itself.
        # visited guards against pre-existing cycles introduced out-of-band (git pull).
        visited: set[str] = set()
        current: ConceptId | None = parent_id
        while current is not None:
            if current == concept_id:
                raise InvalidParent(f"parent chain of {concept_id.value!r} forms a cycle")
            if current.value in visited:
                return
            visited.add(current.value)
            ancestor = self.repo.find_lesson(current)
            current = ancestor.parent_id if ancestor is not None else None

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
