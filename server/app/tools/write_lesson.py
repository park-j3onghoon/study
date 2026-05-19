import datetime as dt
from typing import Any

from .. import storage
from ..validation import is_valid_concept_id
from . import register_tool
from .base import Tool


@register_tool
class WriteLesson(Tool):
    name = "write_lesson"
    description = (
        "Create a new lesson for the user. The lesson_html must be a fully self-contained HTML "
        "document with <!DOCTYPE>, <meta viewport>, inline CSS/SVG, dark-mode support, and an "
        "answer-input form for each question (input/textarea with id matching question id). "
        "Use this when the user explicitly asks to learn a concept."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "concept_id": {
                "type": "string",
                "description": "URL-safe slug. Lowercase, digits, hyphens only. e.g. 'aip-134-update'.",
            },
            "title": {"type": "string", "description": "Human-readable title."},
            "lesson_html": {
                "type": "string",
                "description": "Full self-contained HTML (no external CDN, inline styles/scripts).",
            },
            "questions": {
                "type": "array",
                "description": "Question metadata used later for grading.",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "e.g. 'q1', 'q2'."},
                        "type": {"type": "string", "enum": ["multiple_choice", "short_answer"]},
                        "prompt": {"type": "string"},
                        "options": {"type": "array", "items": {"type": "string"}},
                        "correct": {"type": "string", "description": "Correct option label, for multiple_choice."},
                        "expected_keywords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Keywords expected in a correct short_answer.",
                        },
                    },
                    "required": ["id", "type", "prompt"],
                },
            },
            "model": {"type": "string", "description": "Claude model that generated this lesson."},
            "thinking_budget": {"type": "integer", "description": "Extended-thinking budget used."},
        },
        "required": ["concept_id", "title", "lesson_html", "questions"],
    }

    async def execute(self, input: dict[str, Any]) -> str:
        concept_id = input["concept_id"]
        if not is_valid_concept_id(concept_id):
            return f"Error: invalid concept_id {concept_id!r}. Use lowercase letters/digits/hyphens only."
        lesson_dir = storage.lessons_root() / concept_id
        storage.write_text(lesson_dir / "lesson.html", input["lesson_html"])
        storage.write_json(lesson_dir / "meta.json", {
            "concept_id": concept_id,
            "title": input["title"],
            "created": dt.datetime.now(dt.timezone.utc).isoformat(),
            "model": input.get("model"),
            "thinking_budget": input.get("thinking_budget"),
            "questions": input["questions"],
        })
        return f"Created lesson at lessons/{concept_id}/lesson.html ({len(input['questions'])} questions)."
