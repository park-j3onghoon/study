"""Lessons REST endpoints. Depends only on LessonService."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from ...application.lesson_service import LessonService
from ...domain.exceptions import InvalidConceptId, LessonNotFound
from ...domain.models import ConceptId, Lesson, Result
from ..schemas import AnswersPayload, LessonDTO, LessonSummaryDTO, QuestionDTO, QuestionResultDTO, ResultDTO


def make_router(service: LessonService) -> APIRouter:
    router = APIRouter(prefix="/lessons")

    @router.get("")
    async def list_lessons() -> list[LessonSummaryDTO]:
        return [
            LessonSummaryDTO(
                concept_id=s.concept_id.value,
                title=s.title,
                created=s.created.isoformat(),
                graded=s.graded,
            )
            for s in service.list_summaries()
        ]

    @router.get("/{concept_id}")
    async def get_lesson(concept_id: str) -> LessonDTO:
        lesson = _get_or_404(service, concept_id)
        return _lesson_to_dto(lesson)

    @router.get("/{concept_id}/raw_html", response_class=HTMLResponse)
    async def get_raw_html(concept_id: str) -> str:
        return _get_or_404(service, concept_id).html

    @router.post("/{concept_id}/answers")
    async def save_answers(concept_id: str, payload: AnswersPayload) -> dict:
        cid = _parse_concept_id(concept_id)
        try:
            service.save_answers(cid, payload.answers)
        except LessonNotFound:
            raise HTTPException(status_code=404, detail=f"Lesson not found: {concept_id}")
        return {"status": "saved", "path": f"lessons/{concept_id}/answers.json"}

    @router.get("/{concept_id}/result")
    async def get_result(concept_id: str) -> ResultDTO:
        cid = _parse_concept_id(concept_id)
        result = service.find_result(cid)
        if result is None:
            raise HTTPException(status_code=404, detail=f"Result not found for: {concept_id}")
        return _result_to_dto(result)

    return router


def _parse_concept_id(value: str) -> ConceptId:
    try:
        return ConceptId(value)
    except InvalidConceptId:
        raise HTTPException(status_code=400, detail=f"Invalid concept_id: {value!r}")


def _get_or_404(service: LessonService, value: str) -> Lesson:
    cid = _parse_concept_id(value)
    try:
        return service.get(cid)
    except LessonNotFound:
        raise HTTPException(status_code=404, detail=f"Lesson not found: {value}")


def _lesson_to_dto(lesson: Lesson) -> LessonDTO:
    return LessonDTO(
        concept_id=lesson.concept_id.value,
        title=lesson.title,
        created=lesson.created.isoformat(),
        model=lesson.model,
        thinking_budget=lesson.thinking_budget,
        questions=[
            QuestionDTO(
                id=q.id,
                type=q.type,
                prompt=q.prompt,
                options=list(q.options) if q.options else None,
                correct=q.correct,
                expected_keywords=list(q.expected_keywords) if q.expected_keywords else None,
            )
            for q in lesson.questions
        ],
        lesson_html=lesson.html,
    )


def _result_to_dto(result: Result) -> ResultDTO:
    return ResultDTO(
        graded_at=result.graded_at.isoformat(),
        score=result.score,
        by_question=[
            QuestionResultDTO(id=qr.question_id, correct=qr.correct, comment=qr.comment)
            for qr in result.by_question
        ],
        weakness_tags=list(result.weakness_tags),
        recommendation=result.recommendation,
    )
