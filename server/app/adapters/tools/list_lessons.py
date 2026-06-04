"""list_lessons tool. Returns a sidebar-style summary text."""
from typing import Any

from ...application.lesson_service import LessonService
from ...domain.ports import Tool


class ListLessonsTool(Tool):
    name = "list_lessons"
    description = (
        "List all existing lessons (concept_id, title, created, graded, parent). "
        "parent is the parent lesson's concept_id, or '-' for a root node. "
        "Use this when the user asks 'what have I studied?' or before suggesting a new lesson."
    )
    input_schema = {"type": "object", "properties": {}}

    def __init__(self, service: LessonService):
        self.service = service

    async def execute(self, args: dict[str, Any]) -> str:
        summaries = self.service.list_summaries()
        if not summaries:
            return "(no lessons yet)"
        return "\n".join(
            f"- {s.concept_id.value} | {s.title} | created={s.created.isoformat()} "
            f"| graded={s.graded} | parent={s.parent_id.value if s.parent_id else '-'}"
            for s in summaries
        )
