"""DiskLessonRepository + DiskConversationRepository round-trip."""
from datetime import datetime, timezone

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
