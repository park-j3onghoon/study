import datetime as dt
from typing import Any

from .. import storage
from ..validation import is_valid_concept_id
from . import register_tool
from .base import Tool


@register_tool
class GradeLesson(Tool):
    name = "grade_lesson"
    description = (
        "Save grading results to lessons/{concept_id}/result.json. "
        "Call this after reading the user's answers and evaluating each question. "
        "Include weakness_tags using the study weakness catalog (#tech/용어혼동, #tech/엣지케이스, etc.)."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "concept_id": {"type": "string"},
            "score": {"type": "string", "description": "e.g. '8/10'."},
            "by_question": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "correct": {"type": "boolean"},
                        "comment": {"type": "string", "description": "Why right/wrong, what was the gap."},
                    },
                    "required": ["id", "correct"],
                },
            },
            "weakness_tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "From study weakness catalog. e.g. ['#tech/용어혼동']",
            },
            "recommendation": {
                "type": "string",
                "description": "Whether and what additional study is recommended.",
            },
        },
        "required": ["concept_id", "score", "by_question"],
    }

    async def execute(self, input: dict[str, Any]) -> str:
        concept_id = input["concept_id"]
        if not is_valid_concept_id(concept_id):
            return f"Error: invalid concept_id {concept_id!r}."
        path = storage.lessons_root() / concept_id / "result.json"
        storage.write_json(path, {
            "graded_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "score": input["score"],
            "by_question": input["by_question"],
            "weakness_tags": input.get("weakness_tags", []),
            "recommendation": input.get("recommendation", ""),
        })
        return f"Saved result at lessons/{concept_id}/result.json (score: {input['score']})."
