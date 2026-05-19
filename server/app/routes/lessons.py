"""학습지 REST 엔드포인트. 프론트엔드(P3+)가 호출.
- GET /api/lessons           — 사이드바용 목록
- GET /api/lessons/{id}      — 학습지 본문 (lesson.html + meta)
- POST /api/lessons/{id}/answers — 사용자 답 저장
- GET /api/lessons/{id}/result   — 채점 결과
"""
import datetime as dt

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .. import storage
from ..validation import is_valid_concept_id


router = APIRouter(prefix="/lessons")


class AnswersPayload(BaseModel):
    answers: dict


def _ensure_valid(concept_id: str) -> None:
    if not is_valid_concept_id(concept_id):
        raise HTTPException(status_code=400, detail=f"Invalid concept_id: {concept_id!r}")


@router.get("")
async def list_lessons() -> list[dict]:
    root = storage.lessons_root()
    lessons: list[dict] = []
    for lesson_dir in sorted(root.iterdir()):
        if not lesson_dir.is_dir():
            continue
        meta_path = lesson_dir / "meta.json"
        if not meta_path.exists():
            continue
        meta = storage.read_json(meta_path)
        result_path = lesson_dir / "result.json"
        lessons.append({
            "concept_id": meta["concept_id"],
            "title": meta["title"],
            "created": meta["created"],
            "graded": result_path.exists(),
        })
    return lessons


@router.get("/{concept_id}")
async def get_lesson(concept_id: str) -> dict:
    _ensure_valid(concept_id)
    lesson_dir = storage.lessons_root() / concept_id
    meta_path = lesson_dir / "meta.json"
    html_path = lesson_dir / "lesson.html"
    if not meta_path.exists() or not html_path.exists():
        raise HTTPException(status_code=404, detail=f"Lesson not found: {concept_id}")
    return {
        "meta": storage.read_json(meta_path),
        "lesson_html": storage.read_text(html_path),
    }


@router.post("/{concept_id}/answers")
async def save_answers(concept_id: str, payload: AnswersPayload) -> dict:
    _ensure_valid(concept_id)
    lesson_dir = storage.lessons_root() / concept_id
    if not (lesson_dir / "meta.json").exists():
        raise HTTPException(status_code=404, detail=f"Lesson not found: {concept_id}")
    storage.write_json(lesson_dir / "answers.json", {
        "submitted_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "answers": payload.answers,
    })
    return {"status": "saved", "path": f"lessons/{concept_id}/answers.json"}


@router.get("/{concept_id}/result")
async def get_result(concept_id: str) -> dict:
    _ensure_valid(concept_id)
    result_path = storage.lessons_root() / concept_id / "result.json"
    if not result_path.exists():
        raise HTTPException(status_code=404, detail=f"Result not found for: {concept_id}")
    return storage.read_json(result_path)
