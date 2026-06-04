"""FileEventStream._classify — path → event mapping with the versions/ depth guard."""
from pathlib import Path

from app.adapters.file_event_stream import FileEventStream


class TestClassifyEventType:
    """Interesting files exactly one level deep map to the right event type."""

    def _stream(self, tmp_path: Path) -> FileEventStream:
        return FileEventStream(tmp_path / "lessons")

    def test_meta_json_is_lesson_changed(self, tmp_path):
        stream = self._stream(tmp_path)
        path = stream.lessons_root / "rfc-3986" / "meta.json"
        assert stream._classify(path) == {"type": "lesson_changed", "concept_id": "rfc-3986"}

    def test_result_json_is_lesson_graded(self, tmp_path):
        stream = self._stream(tmp_path)
        path = stream.lessons_root / "rfc-3986" / "result.json"
        assert stream._classify(path) == {"type": "lesson_graded", "concept_id": "rfc-3986"}

    def test_answers_json_is_lesson_answered(self, tmp_path):
        stream = self._stream(tmp_path)
        path = stream.lessons_root / "rfc-3986" / "answers.json"
        assert stream._classify(path) == {"type": "lesson_answered", "concept_id": "rfc-3986"}


class TestClassifyDepthGuard:
    """The depth guard keeps archive snapshots and stray files from firing events."""

    def _stream(self, tmp_path: Path) -> FileEventStream:
        return FileEventStream(tmp_path / "lessons")

    def test_versioned_snapshot_yields_no_event(self, tmp_path):
        # Interesting filename, but nested under versions/{ts}/ → two levels too deep.
        stream = self._stream(tmp_path)
        path = stream.lessons_root / "rfc-3986" / "versions" / "20260101T000000Z" / "meta.json"
        assert stream._classify(path) is None

    def test_uninteresting_filename_yields_no_event(self, tmp_path):
        # Right depth, wrong name → filtered out before the depth check.
        stream = self._stream(tmp_path)
        path = stream.lessons_root / "rfc-3986" / "lesson.html"
        assert stream._classify(path) is None

    def test_file_directly_under_root_yields_no_event(self, tmp_path):
        # Too shallow: parent.parent is the filesystem root, not lessons_root.
        stream = self._stream(tmp_path)
        path = stream.lessons_root / "meta.json"
        assert stream._classify(path) is None
