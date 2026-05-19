import json
from typing import Any

from .. import storage
from ..validation import is_valid_concept_id
from . import register_tool
from .base import Tool


@register_tool
class ReadAnswers(Tool):
    name = "read_answers"
    description = (
        "Read the user's submitted answers for a lesson. "
        "Returns the JSON document at lessons/{concept_id}/answers.json as text. "
        "Use this before grading. If the file does not exist, returns a 'not submitted yet' message."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "concept_id": {"type": "string"},
        },
        "required": ["concept_id"],
    }

    async def execute(self, input: dict[str, Any]) -> str:
        concept_id = input["concept_id"]
        if not is_valid_concept_id(concept_id):
            return f"Error: invalid concept_id {concept_id!r}."
        path = storage.lessons_root() / concept_id / "answers.json"
        if not path.exists():
            return f"No answers submitted yet for {concept_id!r}."
        return json.dumps(storage.read_json(path), ensure_ascii=False, indent=2)
