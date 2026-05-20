"""list_lessons tool. Returns a sidebar-style summary text."""
from typing import Any

from ...application.lesson_service import LessonService
from ...domain.ports import Tool


class ListLessonsTool(Tool):
    name = "list_lessons"
    description = (
        "List all existing lessons (concept_id, title, created, graded). "
        "Use this when the user asks 'what have I studied?' or before suggesting a new lesson."
    )
    input_schema = {"type": "object", "properties": {}}

    def __init__(self, service: LessonService):
        self.service = service

    async def execute(self, _input: dict[str, Any]) -> str:
        summaries = self.service.list_summaries()
        if not summaries:
            return "(no lessons yet)"
        return "\n".join(
            f"- {s.concept_id.value} | {s.title} | created={s.created.isoformat()} | graded={s.graded}"
            for s in summaries
        )
