"""Agent tool adapters — execute() behavior only (input_schema/description are builtins)."""
from dataclasses import replace

import pytest

from app.adapters.tools.list_lessons import ListLessonsTool
from app.adapters.tools.read_lesson import ReadLessonTool
from app.adapters.tools.write_lesson import WriteLessonTool
from app.application.lesson_service import LessonService
from app.domain.models import ConceptId, Result


_VALID_HTML = "<!DOCTYPE html><html><body>hi</body></html>"


def _args(**overrides):
    base = {
        "concept_id": "rfc-3986",
        "title": "RFC 3986",
        "lesson_html": _VALID_HTML,
        "questions": [
            {"id": "q1", "type": "short_answer", "prompt": "Explain URIs"},
        ],
    }
    base.update(overrides)
    return base


@pytest.fixture
def write_tool(tmp_lessons_repo):
    return WriteLessonTool(LessonService(tmp_lessons_repo))


class TestWriteLessonSuccess:
    async def test_valid_lesson_returns_created_and_persists(self, write_tool, tmp_lessons_repo):
        out = await write_tool.execute(_args())
        assert out.startswith("Created")
        assert tmp_lessons_repo.find_lesson(ConceptId("rfc-3986")) is not None

    async def test_parent_id_is_persisted(self, write_tool, tmp_lessons_repo, sample_lesson):
        tmp_lessons_repo.save(sample_lesson)  # the parent must exist (service rejects dangling)
        out = await write_tool.execute(_args(parent_id=sample_lesson.concept_id.value))
        assert out.startswith("Created")
        saved = tmp_lessons_repo.find_lesson(ConceptId("rfc-3986"))
        assert saved.parent_id == sample_lesson.concept_id

    async def test_omitted_parent_id_is_none(self, write_tool, tmp_lessons_repo):
        await write_tool.execute(_args())  # no parent_id key
        assert tmp_lessons_repo.find_lesson(ConceptId("rfc-3986")).parent_id is None

    async def test_blank_parent_id_is_none(self, write_tool, tmp_lessons_repo):
        # Falsy parent_id ("") must behave like omission, not an invalid-id error.
        await write_tool.execute(_args(parent_id=""))
        assert tmp_lessons_repo.find_lesson(ConceptId("rfc-3986")).parent_id is None

    async def test_focus_flag_is_accepted_and_ignored_by_execute(self, write_tool, tmp_lessons_repo):
        # focus is consumed at the agent layer (claude_sdk_agent), not here — execute must
        # accept it without error and persist the lesson normally.
        out = await write_tool.execute(_args(focus=True))
        assert out.startswith("Created")
        assert tmp_lessons_repo.find_lesson(ConceptId("rfc-3986")) is not None


class TestWriteLessonRejection:
    async def test_truncated_html_is_rejected_and_not_saved(self, write_tool, tmp_lessons_repo):
        # No closing </html> → treated as a truncated generation; must not persist.
        out = await write_tool.execute(_args(lesson_html="<!DOCTYPE html><html><body>cut off"))
        assert out.startswith("Error:")
        assert tmp_lessons_repo.find_lesson(ConceptId("rfc-3986")) is None

    async def test_trailing_whitespace_after_html_is_accepted(self, write_tool):
        # The completeness check strips/lowercases, so trailing newline is fine.
        out = await write_tool.execute(_args(lesson_html=_VALID_HTML + "\n  "))
        assert out.startswith("Created")

    async def test_invalid_concept_id_is_rejected(self, write_tool, tmp_lessons_repo):
        out = await write_tool.execute(_args(concept_id="Bad Id"))
        assert out.startswith("Error:")

    async def test_invalid_parent_id_is_rejected(self, write_tool):
        out = await write_tool.execute(_args(parent_id="Bad Parent"))
        assert out.startswith("Error:")

    async def test_dangling_parent_is_rejected(self, write_tool, tmp_lessons_repo):
        # Valid slug but no such lesson on disk → service raises InvalidParent → Error.
        out = await write_tool.execute(_args(parent_id="ghost-parent"))
        assert out.startswith("Error:")
        assert tmp_lessons_repo.find_lesson(ConceptId("rfc-3986")) is None

    async def test_invalid_question_is_rejected(self, write_tool, tmp_lessons_repo):
        bad_q = [{"id": "q1", "type": "multiple_choice", "prompt": "?", "options": ["only"]}]
        out = await write_tool.execute(_args(questions=bad_q))
        assert out.startswith("Error:")
        assert tmp_lessons_repo.find_lesson(ConceptId("rfc-3986")) is None


class TestListLessonsTool:
    async def test_empty_returns_placeholder(self, tmp_lessons_repo):
        out = await ListLessonsTool(LessonService(tmp_lessons_repo)).execute({})
        assert out == "(no lessons yet)"

    async def test_root_lesson_shows_parent_dash(self, tmp_lessons_repo, sample_lesson):
        tmp_lessons_repo.save(sample_lesson)
        out = await ListLessonsTool(LessonService(tmp_lessons_repo)).execute({})
        assert "parent=-" in out
        assert sample_lesson.concept_id.value in out

    async def test_child_lesson_shows_parent_concept_id(self, tmp_lessons_repo, sample_lesson):
        tmp_lessons_repo.save(sample_lesson)
        child = replace(sample_lesson, concept_id=ConceptId("child"),
                        parent_id=sample_lesson.concept_id)
        tmp_lessons_repo.save(child)
        out = await ListLessonsTool(LessonService(tmp_lessons_repo)).execute({})
        assert f"parent={sample_lesson.concept_id.value}" in out


class TestReadLessonTool:
    @pytest.fixture
    def read_tool(self, tmp_lessons_repo):
        return ReadLessonTool(LessonService(tmp_lessons_repo))

    async def test_existing_lesson_returns_metadata_and_html(self, read_tool, tmp_lessons_repo, sample_lesson):
        tmp_lessons_repo.save(sample_lesson)
        out = await read_tool.execute({"concept_id": sample_lesson.concept_id.value})
        assert f"concept_id: {sample_lesson.concept_id.value}" in out
        assert f"title: {sample_lesson.title}" in out
        assert "parent: -" in out          # sample_lesson is a root
        assert "graded: False" in out       # no result.json saved
        assert "q1 [multiple_choice] Pick one" in out
        assert "q2 [short_answer] Explain X" in out   # every question, both types, is listed
        assert "--- lesson_html ---" in out  # header/body separator is part of the contract
        assert sample_lesson.html in out    # full body is returned for dedup

    async def test_child_lesson_shows_parent(self, read_tool, tmp_lessons_repo, sample_lesson):
        tmp_lessons_repo.save(sample_lesson)
        child = replace(sample_lesson, concept_id=ConceptId("child"), parent_id=sample_lesson.concept_id)
        tmp_lessons_repo.save(child)
        out = await read_tool.execute({"concept_id": "child"})
        assert f"parent: {sample_lesson.concept_id.value}" in out

    async def test_graded_lesson_reports_graded_true(self, read_tool, tmp_lessons_repo, sample_lesson):
        tmp_lessons_repo.save(sample_lesson)
        tmp_lessons_repo.save_result(Result(
            concept_id=sample_lesson.concept_id,
            graded_at=sample_lesson.created,
            score="2/2",
            by_question=(),
        ))
        out = await read_tool.execute({"concept_id": sample_lesson.concept_id.value})
        assert "graded: True" in out

    async def test_missing_lesson_returns_not_found(self, read_tool):
        out = await read_tool.execute({"concept_id": "ghost"})
        assert out == "No lesson found for 'ghost'."

    async def test_invalid_concept_id_returns_error(self, read_tool):
        out = await read_tool.execute({"concept_id": "Bad Id"})
        assert out.startswith("Error:")
