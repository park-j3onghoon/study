"""DiskLessonRepository + DiskConversationRepository round-trip."""
from dataclasses import replace
from datetime import datetime, timezone

from app.adapters import _jsonio
from app.domain.models import (
    Answers, Conversation, ConceptId, Question, QuestionResult, Result,
    new_conversation_id,
)


class TestDiskLessonRepository:
    def test_save_and_find_lesson(self, tmp_lessons_repo, sample_lesson):
        tmp_lessons_repo.save(sample_lesson)
        found = tmp_lessons_repo.find_lesson(sample_lesson.concept_id)
        assert found == sample_lesson

    def test_find_lesson_missing_returns_none(self, tmp_lessons_repo):
        assert tmp_lessons_repo.find_lesson(ConceptId("missing")) is None

    def test_exists(self, tmp_lessons_repo, sample_lesson):
        assert not tmp_lessons_repo.exists(sample_lesson.concept_id)
        tmp_lessons_repo.save(sample_lesson)
        assert tmp_lessons_repo.exists(sample_lesson.concept_id)

    def test_list_summaries_skips_corrupt_dirs(self, tmp_lessons_repo, sample_lesson, tmp_path):
        tmp_lessons_repo.save(sample_lesson)
        # add a directory without meta.json — should be ignored
        (tmp_path / "lessons" / "junk").mkdir()
        summaries = tmp_lessons_repo.list_summaries()
        assert len(summaries) == 1
        assert summaries[0].concept_id == sample_lesson.concept_id
        assert summaries[0].graded is False

    def test_answers_round_trip(self, tmp_lessons_repo, sample_lesson):
        tmp_lessons_repo.save(sample_lesson)
        answers = Answers(
            concept_id=sample_lesson.concept_id,
            submitted_at=datetime(2026, 5, 28, 10, tzinfo=timezone.utc),
            values={"q1": "a", "q2": "kw1 stuff"},
        )
        tmp_lessons_repo.save_answers(answers)
        assert tmp_lessons_repo.find_answers(sample_lesson.concept_id) == answers

    def test_result_round_trip_with_accuracy(self, tmp_lessons_repo, sample_lesson):
        tmp_lessons_repo.save(sample_lesson)
        result = Result(
            concept_id=sample_lesson.concept_id,
            graded_at=datetime(2026, 5, 28, 11, tzinfo=timezone.utc),
            score="1/2",
            by_question=(
                QuestionResult(question_id="q1", correct=True),
                QuestionResult(question_id="q2", correct=False, comment="missed kw"),
            ),
            weakness_tags=("#tech/엣지케이스",),
            recommendation="redo q2",
        )
        tmp_lessons_repo.save_result(result)
        found = tmp_lessons_repo.find_result(sample_lesson.concept_id)
        assert found == result
        assert found.accuracy() == 0.5


class TestLessonParentIdPersistence:
    """parent_id round-trip + backward-compat for meta.json written before the field existed."""

    def _strip_parent_key(self, repo, concept_id):
        # Simulate a meta.json from before parent_id existed: the key is entirely absent
        # (NOT present-but-null). This is the real backward-compat shape on disk.
        meta_path = repo._dir(concept_id) / "meta.json"
        meta = _jsonio.read_json(meta_path)
        del meta["parent_id"]
        assert "parent_id" not in meta
        _jsonio.write_json(meta_path, meta)

    def test_parent_id_round_trip(self, tmp_lessons_repo, sample_lesson):
        parent = replace(sample_lesson, concept_id=ConceptId("parent-concept"))
        child = replace(sample_lesson, parent_id=parent.concept_id)
        tmp_lessons_repo.save(parent)
        tmp_lessons_repo.save(child)
        found = tmp_lessons_repo.find_lesson(child.concept_id)
        assert found.parent_id == ConceptId("parent-concept")

    def test_root_lesson_round_trips_with_none_parent(self, tmp_lessons_repo, sample_lesson):
        # parent_id explicitly None (key present, value null) → still None on read.
        tmp_lessons_repo.save(sample_lesson)
        assert tmp_lessons_repo.find_lesson(sample_lesson.concept_id).parent_id is None

    def test_find_lesson_tolerates_missing_parent_key(self, tmp_lessons_repo, sample_lesson):
        # Backward-compat regression (distinct from round-trip): no parent_id key at all.
        tmp_lessons_repo.save(sample_lesson)
        self._strip_parent_key(tmp_lessons_repo, sample_lesson.concept_id)
        found = tmp_lessons_repo.find_lesson(sample_lesson.concept_id)
        assert found is not None  # did not raise on the absent key
        assert found.parent_id is None

    def test_list_summaries_tolerates_missing_parent_key(self, tmp_lessons_repo, sample_lesson):
        tmp_lessons_repo.save(sample_lesson)
        self._strip_parent_key(tmp_lessons_repo, sample_lesson.concept_id)
        summaries = tmp_lessons_repo.list_summaries()
        assert len(summaries) == 1
        assert summaries[0].concept_id == sample_lesson.concept_id
        assert summaries[0].parent_id is None

    def test_corrupt_parent_value_degrades_to_root(self, tmp_lessons_repo, sample_lesson):
        # A git-edited meta.json could hold a value that fails the ConceptId regex.
        # Read must degrade to root (None), not crash.
        tmp_lessons_repo.save(sample_lesson)
        meta_path = tmp_lessons_repo._dir(sample_lesson.concept_id) / "meta.json"
        meta = _jsonio.read_json(meta_path)
        meta["parent_id"] = "Invalid Parent!"
        _jsonio.write_json(meta_path, meta)
        assert tmp_lessons_repo.find_lesson(sample_lesson.concept_id).parent_id is None


class TestArchiveVersion:
    """archive_version snapshots the prior on-disk state under versions/{ts}/."""

    def _versions_dir(self, repo, concept_id):
        return repo._dir(concept_id) / "versions"

    def _graded_lesson(self, repo, sample_lesson):
        repo.save(sample_lesson)
        repo.save_answers(Answers(
            concept_id=sample_lesson.concept_id,
            submitted_at=datetime(2026, 5, 28, 10, tzinfo=timezone.utc),
            values={"q1": "a", "q2": "kw1"},
        ))
        repo.save_result(Result(
            concept_id=sample_lesson.concept_id,
            graded_at=datetime(2026, 5, 28, 11, tzinfo=timezone.utc),
            score="2/2",
            by_question=(
                QuestionResult(question_id="q1", correct=True),
                QuestionResult(question_id="q2", correct=True),
            ),
        ))

    def test_archive_snapshots_all_four_files(self, tmp_lessons_repo, sample_lesson):
        self._graded_lesson(tmp_lessons_repo, sample_lesson)
        tmp_lessons_repo.archive_version(sample_lesson.concept_id)
        versions = list(self._versions_dir(tmp_lessons_repo, sample_lesson.concept_id).iterdir())
        assert len(versions) == 1
        snapshot = versions[0]
        names = sorted(p.name for p in snapshot.iterdir())
        assert names == ["answers.json", "lesson.html", "meta.json", "result.json"]

    def test_archive_skips_files_that_do_not_exist(self, tmp_lessons_repo, sample_lesson):
        # Only the lesson was written (no answers/result). archive copies what exists.
        tmp_lessons_repo.save(sample_lesson)
        tmp_lessons_repo.archive_version(sample_lesson.concept_id)
        snapshot = next(self._versions_dir(tmp_lessons_repo, sample_lesson.concept_id).iterdir())
        names = sorted(p.name for p in snapshot.iterdir())
        assert names == ["lesson.html", "meta.json"]

    def test_list_summaries_does_not_expose_versions(self, tmp_lessons_repo, sample_lesson):
        self._graded_lesson(tmp_lessons_repo, sample_lesson)
        tmp_lessons_repo.archive_version(sample_lesson.concept_id)
        summaries = tmp_lessons_repo.list_summaries()
        # versions/ is a child of the lesson dir, not a sibling top-level dir — invisible.
        assert len(summaries) == 1
        assert summaries[0].concept_id == sample_lesson.concept_id

    def test_archive_clears_live_grading_so_new_version_is_isolated(self, tmp_lessons_repo, sample_lesson):
        # After rotation the snapshot keeps the old grading, but the live dir is reset to
        # ungraded — the incoming rewrite must not inherit the previous score/answers.
        self._graded_lesson(tmp_lessons_repo, sample_lesson)
        tmp_lessons_repo.archive_version(sample_lesson.concept_id)
        cid = sample_lesson.concept_id
        assert tmp_lessons_repo.find_result(cid) is None
        assert tmp_lessons_repo.find_answers(cid) is None
        assert tmp_lessons_repo.find_lesson(cid) is not None  # html/meta stay until save() overwrites
        assert tmp_lessons_repo.list_summaries()[0].graded is False


class TestDiskConversationRepository:
    def _conv(self, **kw):
        defaults = dict(
            id=new_conversation_id(),
            title="t",
            created=datetime(2026, 5, 28, tzinfo=timezone.utc),
            messages=(),
        )
        return Conversation(**(defaults | kw))

    def test_save_and_find(self, tmp_conversations_repo):
        conv = self._conv()
        tmp_conversations_repo.save(conv)
        assert tmp_conversations_repo.find(conv.id) == conv

    def test_find_missing(self, tmp_conversations_repo):
        assert tmp_conversations_repo.find(new_conversation_id()) is None

    def test_list_summaries_newest_first(self, tmp_conversations_repo):
        old = self._conv(title="old", created=datetime(2026, 1, 1, tzinfo=timezone.utc))
        new = self._conv(title="new", created=datetime(2026, 6, 1, tzinfo=timezone.utc))
        tmp_conversations_repo.save(old)
        tmp_conversations_repo.save(new)
        titles = [s.title for s in tmp_conversations_repo.list_summaries()]
        assert titles == ["new", "old"]

    def test_message_count_after_add_turn(self, tmp_conversations_repo):
        conv = self._conv()
        tmp_conversations_repo.save(conv)
        tmp_conversations_repo.save(conv.add_turn("hi", "hey"))
        summary = tmp_conversations_repo.list_summaries()[0]
        assert summary.message_count == 2
