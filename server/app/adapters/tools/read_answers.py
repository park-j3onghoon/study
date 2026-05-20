"""read_answers tool. Returns user's submitted answers as JSON text."""
import json
from typing import Any

from ...application.lesson_service import LessonService
from ...domain.exceptions import InvalidConceptId
from ...domain.models import ConceptId
from ...domain.ports import Tool


class ReadAnswersTool(Tool):
    name = "read_answers"
    description = (
        "Read the user's submitted answers for a lesson. Returns answers as JSON text. "
        "If no answers yet, returns 'No answers submitted yet'. Use this before grading."
    )
    input_schema = {
        "type": "object",
        "properties": {"concept_id": {"type": "string"}},
        "required": ["concept_id"],
    }

    def __init__(self, service: LessonService):
        self.service = service

    async def execute(self, input: dict[str, Any]) -> str:
        try:
            concept_id = ConceptId(input["concept_id"])
        except InvalidConceptId as exc:
            return f"Error: {exc}"
        answers = self.service.find_answers(concept_id)
        if answers is None:
            return f"No answers submitted yet for {concept_id.value!r}."
        return json.dumps(
            {"submitted_at": answers.submitted_at.isoformat(), "answers": answers.values},
            ensure_ascii=False,
            indent=2,
        )
