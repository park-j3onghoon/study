"""Application services — invariants and CQS behavior."""
from dataclasses import replace

import pytest

from app.adapters import _jsonio
from app.domain.exceptions import (
    ConversationNotFound, InvalidParent, LessonNotFound,
)
from app.domain.models import (
    ConceptId, QuestionResult, Result, new_conversation_id,
)
from datetime import datetime, timezone


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


def _named(sample_lesson, cid, **kw):
    return replace(sample_lesson, concept_id=ConceptId(cid), **kw)


def _force_parent_on_disk(repo, concept_id, parent_id):
    # Bypass create() validation to plant a hierarchy that create() would reject.
    # Used to stage a pre-existing on-disk cycle (e.g. from a git pull).
    meta_path = repo._dir(concept_id) / "meta.json"
    meta = _jsonio.read_json(meta_path)
    meta["parent_id"] = parent_id.value
    _jsonio.write_json(meta_path, meta)


class TestLessonServiceHierarchy:
    """create() hierarchy validation: self-parent / dangling / cycle / valid."""

    def test_self_parent_is_rejected_by_domain(self, sample_lesson):
        # The self-parent invariant lives on the model, so construction itself raises —
        # create() never gets the chance.
        with pytest.raises(InvalidParent):
            replace(sample_lesson, parent_id=sample_lesson.concept_id)

    def test_dangling_parent_is_rejected(self, lesson_service, sample_lesson):
        # parent_id present (decision-1 True) but parent absent (exists() False) → raise.
        child = _named(sample_lesson, "child", parent_id=ConceptId("ghost-parent"))
        with pytest.raises(InvalidParent):
            lesson_service.create(child)

    def test_valid_parent_is_accepted(self, lesson_service, sample_lesson):
        # parent present AND parent exists → no raise, child persisted with the link.
        lesson_service.create(_named(sample_lesson, "parent-node"))
        lesson_service.create(_named(sample_lesson, "child-node", parent_id=ConceptId("parent-node")))
        assert lesson_service.get(ConceptId("child-node")).parent_id == ConceptId("parent-node")

    def test_root_lesson_skips_parent_checks(self, lesson_service, sample_lesson):
        # parent_id None (decision-1 False) → exists/cycle checks skipped, saves fine.
        lesson_service.create(sample_lesson)
        assert lesson_service.get(sample_lesson.concept_id).parent_id is None

    def test_cycle_is_rejected(self, lesson_service, sample_lesson):
        # a is root, b parents a. Re-creating a with parent=b would close the loop a→b→a.
        lesson_service.create(_named(sample_lesson, "a"))
        lesson_service.create(_named(sample_lesson, "b", parent_id=ConceptId("a")))
        with pytest.raises(InvalidParent):
            lesson_service.create(_named(sample_lesson, "a", parent_id=ConceptId("b")))

    def test_cycle_walk_terminates_on_preexisting_cycle(self, lesson_service, sample_lesson):
        # Plant an on-disk cycle x→y→x (out-of-band, e.g. git pull), then attach a fresh
        # node z under x. The walk must terminate via the visited-set, not loop forever,
        # and since z is outside the cycle it is accepted.
        repo = lesson_service.repo
        lesson_service.create(_named(sample_lesson, "x"))
        lesson_service.create(_named(sample_lesson, "y", parent_id=ConceptId("x")))
        _force_parent_on_disk(repo, ConceptId("x"), ConceptId("y"))  # now x→y→x
        lesson_service.create(_named(sample_lesson, "z", parent_id=ConceptId("x")))
        assert lesson_service.get(ConceptId("z")).parent_id == ConceptId("x")


class TestLessonServiceArchive:
    """archive policy: only when the existing lesson exists AND is graded (MC/DC on the AND)."""

    def _grade(self, repo, concept_id):
        repo.save_result(Result(
            concept_id=concept_id,
            graded_at=datetime(2026, 5, 28, 11, tzinfo=timezone.utc),
            score="2/2",
            by_question=(QuestionResult(question_id="q1", correct=True),),
        ))

    def _versions(self, repo, concept_id):
        vdir = repo._dir(concept_id) / "versions"
        return list(vdir.iterdir()) if vdir.exists() else []

    def test_graded_overwrite_archives_and_isolates_new_version(self, lesson_service, sample_lesson):
        # exists=True AND graded=True → archive fires.
        repo = lesson_service.repo
        lesson_service.create(sample_lesson)
        repo.save_answers(sample_lesson.submit_answers(
            {"q1": "a"}, datetime(2026, 5, 28, 10, tzinfo=timezone.utc)))
        self._grade(repo, sample_lesson.concept_id)

        rewritten = replace(sample_lesson, title="Rewritten", html="<html>new</html>")
        lesson_service.create(rewritten)

        # archived snapshot exists with the OLD result/answers preserved...
        snapshot = self._versions(repo, sample_lesson.concept_id)
        assert len(snapshot) == 1
        archived_names = sorted(p.name for p in snapshot[0].iterdir())
        assert "result.json" in archived_names and "answers.json" in archived_names
        # ...and the new live lesson reflects the rewrite (old result not merged in).
        assert lesson_service.get(sample_lesson.concept_id).title == "Rewritten"

    def test_ungraded_overwrite_does_not_archive(self, lesson_service, sample_lesson):
        # exists=True AND graded=False → second operand flips decision False → no archive.
        repo = lesson_service.repo
        lesson_service.create(sample_lesson)
        assert repo.find_result(sample_lesson.concept_id) is None  # ungraded
        lesson_service.create(replace(sample_lesson, title="Redo"))
        assert self._versions(repo, sample_lesson.concept_id) == []
        assert lesson_service.get(sample_lesson.concept_id).title == "Redo"

    def test_first_create_does_not_archive(self, lesson_service, sample_lesson):
        # exists=False → first operand flips decision False → no archive on a brand-new lesson.
        repo = lesson_service.repo
        lesson_service.create(sample_lesson)
        assert self._versions(repo, sample_lesson.concept_id) == []


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
