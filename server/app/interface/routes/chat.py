"""Chat endpoints (SSE streaming). Depends only on ChatService."""
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ...application.chat_service import ChatService
from ...domain.exceptions import InvalidConversationId
from ...domain.models import ConversationId
from ..schemas import ChatRequest


def make_router(chat_service: ChatService) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    async def health() -> dict:
        return {"status": "ok"}

    @router.post("/chat")
    async def chat(req: ChatRequest) -> StreamingResponse:
        conv_id = _parse_conversation_id(req.conversation_id)

        async def generate():
            try:
                async for event in chat_service.stream(
                    messages=req.messages,
                    model=req.model,
                    thinking_budget=req.thinking_budget,
                    conversation_id=conv_id,
                ):
                    event_name = event.pop("type")
                    yield _format_sse(event_name, event)
            except Exception as exc:
                yield _format_sse("error", {"message": str(exc)})

        headers = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
        return StreamingResponse(generate(), media_type="text/event-stream", headers=headers)

    return router


def _parse_conversation_id(value: str | None) -> ConversationId | None:
    if value is None or value == "":
        return None
    try:
        return ConversationId(value)
    except InvalidConversationId:
        return None  # invalid id면 그냥 conversation 없이 진행


def _format_sse(event_name: str, data: dict) -> str:
    return f"event: {event_name}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
