"""Disk-backed LessonRepository. Stores under {root}/{concept_id}/."""
from datetime import datetime
from pathlib import Path

from ..domain.exceptions import InvalidConceptId
from ..domain.models import (
    Answers, ConceptId, Lesson, LessonSummary, Question, QuestionResult, Result,
)
from ..domain.ports import LessonRepository
from . import _jsonio


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
            ))
        return summaries

    def exists(self, concept_id: ConceptId) -> bool:
        return (self._dir(concept_id) / "meta.json").exists()

    def _dir(self, concept_id: ConceptId) -> Path:
        return self.root / concept_id.value


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
