"""read_lesson tool. Returns an existing lesson's full content for cluster dedup."""
from typing import Any

from ...application.lesson_service import LessonService
from ...domain.exceptions import InvalidConceptId, LessonNotFound
from ...domain.models import ConceptId, Lesson
from ...domain.ports import Tool


class ReadLessonTool(Tool):
    name = "read_lesson"
    description = (
        "Read an existing lesson's full content: its metadata (title, parent, graded status), "
        "its question prompts, and the complete lesson_html body. "
        "Use this BEFORE rewriting a cluster of related lessons — call list_lessons first to find "
        "the parent and siblings (same parent=), then read_lesson each one so you can see exactly "
        "what is already explained and strip globally-duplicated content when you rewrite. "
        "Also call it before synthesizing an answer about something you previously taught, so you "
        "rely on the saved lesson rather than re-deriving it. "
        "Returns a readable text block (metadata header + the full lesson_html). "
        "If no lesson exists for the concept_id, returns 'No lesson found for {id}'. "
        "If concept_id is malformed, returns 'Error: ...'."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "concept_id": {"type": "string", "description": "concept_id of the lesson to read."},
        },
        "required": ["concept_id"],
    }

    def __init__(self, service: LessonService):
        self.service = service

    async def execute(self, args: dict[str, Any]) -> str:
        try:
            concept_id = ConceptId(args["concept_id"])
        except InvalidConceptId as exc:
            return f"Error: {exc}"
        try:
            lesson = self.service.get(concept_id)
        except LessonNotFound:
            return f"No lesson found for {concept_id.value!r}."
        graded = self.service.find_result(concept_id) is not None
        return _render(lesson, graded)


def _render(lesson: Lesson, graded: bool) -> str:
    parent = lesson.parent_id.value if lesson.parent_id else "-"
    header = [
        f"concept_id: {lesson.concept_id.value}",
        f"title: {lesson.title}",
        f"parent: {parent}",
        f"graded: {graded}",
        "questions:",
    ]
    for q in lesson.questions:
        header.append(f"  - {q.id} [{q.type}] {q.prompt}")
    header.append("")
    header.append("--- lesson_html ---")
    header.append(lesson.html)
    return "\n".join(header)
