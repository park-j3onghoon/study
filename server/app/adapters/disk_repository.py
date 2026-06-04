"""Disk-backed LessonRepository. Stores under {root}/{concept_id}/."""
import shutil
from datetime import datetime, timezone
from pathlib import Path

from ..domain.exceptions import InvalidConceptId
from ..domain.models import (
    Answers, ConceptId, Lesson, LessonSummary, Question, QuestionResult, Result,
)
from ..domain.ports import LessonRepository
from . import _jsonio


_VERSIONED_FILES = ("lesson.html", "meta.json", "answers.json", "result.json")


class DiskLessonRepository(LessonRepository):
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    # ── Commands ────────────────────────────────────────────────────────────
    def save(self, lesson: Lesson) -> None:
        lesson_dir = self._dir(lesson.concept_id)
        _jsonio.write_text(lesson_dir / "lesson.html", lesson.html)
        _jsonio.write_json(lesson_dir / "meta.json", {
            "concept_id": lesson.concept_id.value,
            "title": lesson.title,
            "created": lesson.created.isoformat(),
            "model": lesson.model,
            "thinking_budget": lesson.thinking_budget,
            "parent_id": lesson.parent_id.value if lesson.parent_id else None,
            "questions": [_question_to_dict(q) for q in lesson.questions],
        })

    def save_answers(self, answers: Answers) -> None:
        _jsonio.write_json(self._dir(answers.concept_id) / "answers.json", {
            "submitted_at": answers.submitted_at.isoformat(),
            "answers": answers.values,
        })

    def save_result(self, result: Result) -> None:
        _jsonio.write_json(self._dir(result.concept_id) / "result.json", {
            "graded_at": result.graded_at.isoformat(),
            "score": result.score,
            "by_question": [
                {"id": qr.question_id, "correct": qr.correct, "comment": qr.comment}
                for qr in result.by_question
            ],
            "weakness_tags": list(result.weakness_tags),
            "recommendation": result.recommendation,
        })

    def archive_version(self, concept_id: ConceptId) -> None:
        # Rotate the lesson before a rewrite: snapshot current files into versions/{ts}/,
        # then drop the live answers/result so the incoming new version starts ungraded —
        # its questions differ, so the old score no longer applies. lesson.html/meta.json
        # stay (the subsequent save overwrites them). copy2 (not move) survives a failed write.
        # ts carries microseconds so two rotations in the same second don't collide.
        lesson_dir = self._dir(concept_id)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
        version_dir = lesson_dir / "versions" / ts
        version_dir.mkdir(parents=True, exist_ok=True)
        for name in _VERSIONED_FILES:
            src = lesson_dir / name
            if src.exists():
                shutil.copy2(src, version_dir / name)
        for name in ("answers.json", "result.json"):
            (lesson_dir / name).unlink(missing_ok=True)

    # ── Queries ─────────────────────────────────────────────────────────────
    def find_lesson(self, concept_id: ConceptId) -> Lesson | None:
        d = self._dir(concept_id)
        meta_path = d / "meta.json"
        html_path = d / "lesson.html"
        if not meta_path.exists() or not html_path.exists():
            return None
        meta = _jsonio.read_json(meta_path)
        return Lesson(
            concept_id=concept_id,
            title=meta["title"],
            html=_jsonio.read_text(html_path),
            questions=tuple(_question_from_dict(q) for q in meta["questions"]),
            created=datetime.fromisoformat(meta["created"]),
            model=meta.get("model"),
            thinking_budget=meta.get("thinking_budget"),
            parent_id=_parent_id_from_meta(meta),
        )

    def find_answers(self, concept_id: ConceptId) -> Answers | None:
        path = self._dir(concept_id) / "answers.json"
        if not path.exists():
            return None
        data = _jsonio.read_json(path)
        return Answers(
            concept_id=concept_id,
            submitted_at=datetime.fromisoformat(data["submitted_at"]),
            values=data["answers"],
        )

    def find_result(self, concept_id: ConceptId) -> Result | None:
        path = self._dir(concept_id) / "result.json"
        if not path.exists():
            return None
        data = _jsonio.read_json(path)
        return Result(
            concept_id=concept_id,
            graded_at=datetime.fromisoformat(data["graded_at"]),
            score=data["score"],
            by_question=tuple(
                QuestionResult(question_id=qr["id"], correct=qr["correct"], comment=qr.get("comment", ""))
                for qr in data["by_question"]
            ),
            weakness_tags=tuple(data.get("weakness_tags", [])),
            recommendation=data.get("recommendation", ""),
        )

    def list_summaries(self) -> list[LessonSummary]:
        summaries: list[LessonSummary] = []
        for d in sorted(self.root.iterdir()):
            if not d.is_dir() or not (d / "meta.json").exists():
                continue
            meta = _jsonio.read_json(d / "meta.json")
            try:
                cid = ConceptId(meta["concept_id"])
            except (InvalidConceptId, KeyError):
                # 손상된 메타는 건너뛴다 — 사이드바가 죽지 않도록.
                continue
            summaries.append(LessonSummary(
                concept_id=cid,
                title=meta["title"],
                created=datetime.fromisoformat(meta["created"]),
                graded=(d / "result.json").exists(),
                parent_id=_parent_id_from_meta(meta),
            ))
        return summaries

    def exists(self, concept_id: ConceptId) -> bool:
        return (self._dir(concept_id) / "meta.json").exists()

    def _dir(self, concept_id: ConceptId) -> Path:
        return self.root / concept_id.value


def _parent_id_from_meta(meta: dict) -> ConceptId | None:
    # Key absent or null → root. Corrupt value (e.g. git-edited) degrades to root
    # rather than crashing the read — mirrors the corrupt-meta skip in list_summaries.
    raw = meta.get("parent_id")
    if not raw:
        return None
    try:
        return ConceptId(raw)
    except InvalidConceptId:
        return None


def _question_to_dict(q: Question) -> dict:
    return {
        "id": q.id,
        "type": q.type,
        "prompt": q.prompt,
        "options": list(q.options) if q.options is not None else None,
        "correct": q.correct,
        "expected_keywords": list(q.expected_keywords) if q.expected_keywords is not None else None,
    }


def _question_from_dict(d: dict) -> Question:
    return Question(
        id=d["id"],
        type=d["type"],
        prompt=d["prompt"],
        options=tuple(d["options"]) if d.get("options") else None,
        correct=d.get("correct"),
        expected_keywords=tuple(d["expected_keywords"]) if d.get("expected_keywords") else None,
    )
