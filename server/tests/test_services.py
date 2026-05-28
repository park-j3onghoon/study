"""Application services — invariants and CQS behavior."""
import pytest

from app.domain.exceptions import ConversationNotFound, LessonNotFound
from app.domain.models import ConceptId, new_conversation_id


class TestLessonService:
    def test_submit_answers_without_lesson_raises(self, lesson_service):
        with pytest.raises(LessonNotFound):
            lesson_service.submit_answers(ConceptId("nope"), {"q1": "x"})

    def test_submit_answers_filters_unknown_question_ids(self, lesson_service, sample_lesson):
        lesson_service.create(sample_lesson)
        lesson_service.submit_answers(sample_lesson.concept_id, {
            "q1": "a", "q2": "kw1", "ghost": "ignored",
        })
        found = lesson_service.find_answers(sample_lesson.concept_id)
        assert found is not None
        assert found.values == {"q1": "a", "q2": "kw1"}

    def test_get_raises_when_absent(self, lesson_service):
        with pytest.raises(LessonNotFound):
            lesson_service.get(ConceptId("nope"))

    def test_find_answers_returns_none_when_absent(self, lesson_service):
        assert lesson_service.find_answers(ConceptId("nope")) is None


class TestConversationService:
    def test_add_turn_without_conversation_raises(self, conversation_service):
        with pytest.raises(ConversationNotFound):
            conversation_service.add_turn(new_conversation_id(), "u", "a")

    def test_create_then_add_turn(self, conversation_service):
        cid = new_conversation_id()
        conversation_service.create(cid, "t")
        conversation_service.add_turn(cid, "hi", "hey")
        conv = conversation_service.get(cid)
        assert [m["role"] for m in conv.messages] == ["user", "assistant"]
        assert conv.messages[0]["content"] == "hi"
        assert conv.messages[1]["content"] == "hey"

    def test_get_raises_when_absent(self, conversation_service):
        with pytest.raises(ConversationNotFound):
            conversation_service.get(new_conversation_id())

    def test_find_returns_none_when_absent(self, conversation_service):
        assert conversation_service.find(new_conversation_id()) is None
