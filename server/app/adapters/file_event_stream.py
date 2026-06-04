"""File-system backed EventStream. Watches lessons/ for meta.json / result.json changes
and yields domain-level events the UI can react to."""
from pathlib import Path
from typing import AsyncIterator

from watchfiles import awatch

from ..domain.ports import EventStream


_INTERESTING_FILES = {"meta.json", "result.json", "answers.json"}


class FileEventStream(EventStream):
    def __init__(self, lessons_root: Path):
        self.lessons_root = lessons_root
        self.lessons_root.mkdir(parents=True, exist_ok=True)

    async def watch(self) -> AsyncIterator[dict]:
        async for changes in awatch(str(self.lessons_root)):
            for _change_type, raw_path in changes:
                event = self._classify(Path(raw_path))
                if event is not None:
                    yield event

    def _classify(self, path: Path) -> dict | None:
        if path.name not in _INTERESTING_FILES:
            return None
        # Only lessons/{concept_id}/{file} is a real lesson — exactly one level deep.
        # versions/{ts}/{file} archive snapshots are deeper and must not fire events.
        try:
            if path.parent.parent.resolve() != self.lessons_root.resolve():
                return None
            concept_id = path.parent.name
        except Exception:
            return None
        if path.name == "result.json":
            return {"type": "lesson_graded", "concept_id": concept_id}
        if path.name == "answers.json":
            return {"type": "lesson_answered", "concept_id": concept_id}
        return {"type": "lesson_changed", "concept_id": concept_id}
