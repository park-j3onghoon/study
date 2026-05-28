"""write_lesson tool. Delegates to LessonService.create()."""
from datetime import datetime, timezone
from typing import Any

from ...application.lesson_service import LessonService
from ...domain.exceptions import InvalidConceptId, InvalidQuestion
from ...domain.models import ConceptId, Lesson, Question
from ...domain.ports import Tool


class WriteLessonTool(Tool):
    name = "write_lesson"
    description = (
        "Create a new self-contained HTML lesson. The lesson_html must be a complete document "
        "(<!DOCTYPE>, <meta viewport>, inline CSS/SVG, dark-mode support). "
        "It must include a <form id='answer-form'> with one input per question (name=question id) "
        "and an inline <script> that submits to '/api/lessons/{CONCEPT_ID}/answers' via fetch "
        "(same-origin, POST, JSON body {answers: {q1: ..., ...}}). Embed the actual concept_id "
        "value as a JS constant inside the script. Use when the user requests to learn a concept."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "concept_id": {"type": "string", "description": "URL-safe slug (lowercase/digits/hyphens)."},
            "title": {"type": "string"},
            "lesson_html": {"type": "string"},
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "type": {"type": "string", "enum": ["multiple_choice", "short_answer"]},
                        "prompt": {"type": "string"},
                        "options": {"type": "array", "items": {"type": "string"}},
                        "correct": {"type": "string"},
                        "expected_keywords": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["id", "type", "prompt"],
                },
            },
            "model": {"type": "string"},
            "thinking_budget": {"type": "integer"},
        },
        "required": ["concept_id", "title", "lesson_html", "questions"],
    }

    def __init__(self, service: LessonService):
        self.service = service

    async def execute(self, args: dict[str, Any]) -> str:
        try:
            concept_id = ConceptId(args["concept_id"])
        except InvalidConceptId as exc:
            return f"Error: {exc}"
        try:
            questions = tuple(_to_question(q) for q in args["questions"])
        except InvalidQuestion as exc:
            return f"Error: {exc}"
        lesson = Lesson(
            concept_id=concept_id,
            title=args["title"],
            html=args["lesson_html"],
            questions=questions,
            created=datetime.now(timezone.utc),
            model=args.get("model"),
            thinking_budget=args.get("thinking_budget"),
        )
        self.service.create(lesson)
        return f"Created lesson at lessons/{concept_id.value}/lesson.html ({len(lesson.questions)} questions)."


def _to_question(d: dict) -> Question:
    return Question(
        id=d["id"],
        type=d["type"],
        prompt=d["prompt"],
        options=tuple(d["options"]) if d.get("options") else None,
        correct=d.get("correct"),
        expected_keywords=tuple(d["expected_keywords"]) if d.get("expected_keywords") else None,
    )
