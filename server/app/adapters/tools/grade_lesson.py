"""grade_lesson tool. Saves a Result via LessonService."""
from datetime import datetime, timezone
from typing import Any

from ...application.lesson_service import LessonService
from ...domain.exceptions import InvalidConceptId, LessonNotFound
from ...domain.models import ConceptId, QuestionResult, Result
from ...domain.ports import Tool


class GradeLessonTool(Tool):
    name = "grade_lesson"
    description = (
        "Save grading results. Call after read_answers and evaluating each question. "
        "Provide score (e.g. '4/5'), per-question correctness with comment, weakness tags "
        "from the project catalog (#tech/용어혼동, #tech/엣지케이스, etc.), and a recommendation."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "concept_id": {"type": "string"},
            "score": {"type": "string"},
            "by_question": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "correct": {"type": "boolean"},
                        "comment": {"type": "string"},
                    },
                    "required": ["id", "correct"],
                },
            },
            "weakness_tags": {"type": "array", "items": {"type": "string"}},
            "recommendation": {"type": "string"},
        },
        "required": ["concept_id", "score", "by_question"],
    }

    def __init__(self, service: LessonService):
        self.service = service

    async def execute(self, args: dict[str, Any]) -> str:
        try:
            concept_id = ConceptId(args["concept_id"])
        except InvalidConceptId as exc:
            return f"Error: {exc}"
        result = Result(
            concept_id=concept_id,
            graded_at=datetime.now(timezone.utc),
            score=args["score"],
            by_question=tuple(
                QuestionResult(question_id=q["id"], correct=q["correct"], comment=q.get("comment", ""))
                for q in args["by_question"]
            ),
            weakness_tags=tuple(args.get("weakness_tags", [])),
            recommendation=args.get("recommendation", ""),
        )
        try:
            self.service.save_result(result)
        except LessonNotFound as exc:
            return f"Error: {exc}"
        return f"Saved result at lessons/{concept_id.value}/result.json (score: {result.score})."
