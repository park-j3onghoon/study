"""Domain invariants — frozen models, validation, behavior methods."""
from datetime import datetime, timezone

import pytest

from app.domain.exceptions import (
    InvalidConceptId, InvalidConversationId, InvalidQuestion,
)
from app.domain.models import (
    ConceptId, Conversation, ConversationId, Lesson, Question, QuestionResult,
    Result, new_conversation_id,
)


class TestConceptId:
    def test_accepts_lowercase_slug(self):
        assert ConceptId("rfc-3986").value == "rfc-3986"

    def test_accepts_digits_only(self):
        assert ConceptId("123").value == "123"

    @pytest.mark.parametrize("bad", ["RFC", "with space", "with_under", "-leading-hyphen", "", "a/b", "../etc"])
    def test_rejects_invalid(self, bad):
        with pytest.raises(InvalidConceptId):
            ConceptId(bad)


class TestConversationId:
    def test_accepts_uuid_hex(self):
        cid = new_conversation_id()
        assert len(cid.value) == 32

    @pytest.mark.parametrize("bad", [
        "",
        "short",
        "../etc/passwd",
        "/absolute",
        "abc.def",
        "G" * 32,  # uppercase not allowed
        "0" * 31,  # too short
        "0" * 33,  # too long
    ])
    def test_rejects_invalid(self, bad):
        with pytest.raises(InvalidConversationId):
            ConversationId(bad)


class TestQuestion:
    def test_multiple_choice_requires_options(self):
        with pytest.raises(InvalidQuestion):
            Question(id="q", type="multiple_choice", prompt="?", options=None)

    def test_multiple_choice_requires_at_least_two_options(self):
        with pytest.raises(InvalidQuestion):
            Question(id="q", type="multiple_choice", prompt="?", options=("only",))

    def test_multiple_choice_correct_must_be_in_options(self):
        with pytest.raises(InvalidQuestion):
            Question(id="q", type="multiple_choice", prompt="?",
                     options=("a", "b"), correct="c")

    def test_short_answer_does_not_require_options(self):
        q = Question(id="q", type="short_answer", prompt="explain")
        assert q.options is None

    def test_rejects_unknown_type(self):
        with pytest.raises(InvalidQuestion):
            Question(id="q", type="essay", prompt="?")  # type: ignore[arg-type]

    def test_rejects_empty_id(self):
        with pytest.raises(InvalidQuestion):
            Question(id="", type="short_answer", prompt="?")

    def test_rejects_empty_prompt(self):
        with pytest.raises(InvalidQuestion):
            Question(id="q", type="short_answer", prompt="")


class TestLessonSubmitAnswers:
    def _lesson(self):
        return Lesson(
            concept_id=ConceptId("c"),
            title="t",
            html="",
            questions=(
                Question(id="q1", type="short_answer", prompt="?"),
                Question(id="q2", type="short_answer", prompt="?"),
            ),
            created=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )

    def test_filters_out_unknown_question_ids(self):
        answers = self._lesson().submit_answers(
            {"q1": "x", "q2": "y", "stranger": "z"},
            datetime(2026, 1, 2, tzinfo=timezone.utc),
        )
        assert answers.values == {"q1": "x", "q2": "y"}

    def test_preserves_submitted_at(self):
        at = datetime(2026, 1, 2, 12, 30, tzinfo=timezone.utc)
        answers = self._lesson().submit_answers({"q1": "x"}, at)
        assert answers.submitted_at == at


class TestResultAccuracy:
    def _result(self, by_question):
        return Result(
            concept_id=ConceptId("c"),
            graded_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            score="x",
            by_question=tuple(by_question),
        )

    def test_empty_is_zero(self):
        assert self._result([]).accuracy() == 0.0

    def test_all_correct(self):
        r = self._result([
            QuestionResult(question_id="q1", correct=True),
            QuestionResult(question_id="q2", correct=True),
        ])
        assert r.accuracy() == 1.0
        assert r.total_correct() == 2
        assert r.total() == 2

    def test_partial(self):
        r = self._result([
            QuestionResult(question_id="q1", correct=True),
            QuestionResult(question_id="q2", correct=False),
            QuestionResult(question_id="q3", correct=True),
        ])
        assert r.accuracy() == pytest.approx(2 / 3)


class TestConversationAddTurn:
    def _conv(self):
        return Conversation(
            id=new_conversation_id(),
            title="t",
            created=datetime(2026, 1, 1, tzinfo=timezone.utc),
            messages=(),
        )

    def test_appends_both_sides(self):
        out = self._conv().add_turn("hi", "hey")
        assert out.messages == (
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hey"},
        )

    def test_skips_empty_user(self):
        out = self._conv().add_turn("", "hey")
        assert out.messages == ({"role": "assistant", "content": "hey"},)

    def test_skips_empty_assistant(self):
        out = self._conv().add_turn("hi", "")
        assert out.messages == ({"role": "user", "content": "hi"},)

    def test_both_empty_is_noop(self):
        c = self._conv()
        assert c.add_turn("", "") is c or c.add_turn("", "").messages == ()
