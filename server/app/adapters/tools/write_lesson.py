"""write_lesson tool. Delegates to LessonService.create()."""
import logging
from datetime import datetime, timezone
from typing import Any

from ...application.lesson_service import LessonService
from ...domain.exceptions import InvalidConceptId, InvalidParent, InvalidQuestion
from ...domain.models import ConceptId, Lesson, Question
from ...domain.ports import Tool


log = logging.getLogger(__name__)


class WriteLessonTool(Tool):
    name = "write_lesson"
    description = (
        "Create a new self-contained HTML lesson. The lesson_html must be a complete document "
        "(<!DOCTYPE>, <meta viewport>, inline CSS/SVG, dark-mode support). "
        "It must include a <form id='answer-form'> with one input per question (name=question id) "
        "and an inline <script> that submits to '/api/lessons/{CONCEPT_ID}/answers' via fetch "
        "(same-origin, POST, JSON body {answers: {q1: ..., ...}}). Embed the actual concept_id "
        "value as a JS constant inside the script. Use when the user requests to learn a concept. "
        "parent_id: concept_id of the parent lesson this one nests under in the tree (omit for a root node). "
        "focus: true when this is the lesson the user actually asked for, so the UI auto-opens it "
        "(false for sibling/parent lessons rewritten as a side effect)."
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
            "parent_id": {
                "type": "string",
                "description": "concept_id of the parent lesson in the tree; omit for a root node.",
            },
            "focus": {
                "type": "boolean",
                "description": "true if the UI should auto-open this lesson (the one the user asked for).",
            },
        },
        "required": ["concept_id", "title", "lesson_html", "questions"],
    }

    def __init__(self, service: LessonService):
        self.service = service

    async def execute(self, args: dict[str, Any]) -> str:
        try:
            concept_id = ConceptId(args["concept_id"])
        except InvalidConceptId as exc:
            log.warning("write_lesson rejected: invalid concept_id %r — %s", args.get("concept_id"), exc)
            return f"Error: {exc}"
        parent_value = args.get("parent_id")
        try:
            parent_id = ConceptId(parent_value) if parent_value else None
        except InvalidConceptId as exc:
            log.warning("write_lesson rejected: invalid parent_id %r — %s", parent_value, exc)
            return f"Error: {exc}"
        html = args["lesson_html"]
        # Reject lessons truncated by max_response_tokens: a complete document ends with </html>.
        if not html.strip().lower().endswith("</html>"):
            log.warning("write_lesson rejected: incomplete html for %r (no </html>)", concept_id.value)
            return "Error: lesson_html is incomplete (must end with </html>); it was likely truncated — regenerate it shorter."
        try:
            questions = tuple(_to_question(q) for q in args["questions"])
        except InvalidQuestion as exc:
            log.warning("write_lesson rejected: invalid question — %s", exc)
            return f"Error: {exc}"
        lesson = Lesson(
            concept_id=concept_id,
            title=args["title"],
            html=html,
            questions=questions,
            created=datetime.now(timezone.utc),
            model=args.get("model"),
            thinking_budget=args.get("thinking_budget"),
            parent_id=parent_id,
        )
        try:
            self.service.create(lesson)
        except InvalidParent as exc:
            log.warning("write_lesson rejected: invalid parent for %r — %s", concept_id.value, exc)
            return f"Error: {exc}"
        except Exception as exc:
            log.exception("write_lesson failed to save %r", concept_id.value)
            return f"Error: failed to save lesson: {exc}"
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
