from typing import Any

from .. import storage
from . import register_tool
from .base import Tool


@register_tool
class ListLessons(Tool):
    name = "list_lessons"
    description = (
        "List all existing lessons with their titles, creation dates, and grading status. "
        "Use this when the user asks 'what have I studied?' or to provide context "
        "before suggesting a new lesson."
    )
    input_schema = {"type": "object", "properties": {}}

    async def execute(self, input: dict[str, Any]) -> str:
        root = storage.lessons_root()
        lessons: list[dict] = []
        for lesson_dir in sorted(root.iterdir()):
            if not lesson_dir.is_dir():
                continue
            meta_path = lesson_dir / "meta.json"
            if not meta_path.exists():
                continue
            meta = storage.read_json(meta_path)
            result_path = lesson_dir / "result.json"
            score = storage.read_json(result_path)["score"] if result_path.exists() else None
            lessons.append({
                "concept_id": meta["concept_id"],
                "title": meta["title"],
                "created": meta["created"],
                "graded": result_path.exists(),
                "score": score,
            })
        if not lessons:
            return "(no lessons yet)"
        return "\n".join(
            f"- {x['concept_id']} | {x['title']} | created={x['created']} | graded={x['graded']} | score={x['score']}"
            for x in lessons
        )
