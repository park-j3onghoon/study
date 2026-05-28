"""Chat endpoints (SSE streaming). Depends on ChatService + ConversationService."""
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ...application.chat_service import ChatService
from ...application.conversation_service import ConversationService
from ...domain.exceptions import ConversationNotFound, InvalidConversationId
from ...domain.models import ConversationId
from ..schemas import ChatRequest
from ..sse import SSE_HEADERS, format_event


log = logging.getLogger(__name__)


def make_router(chat_service: ChatService, conversation_service: ConversationService) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    async def health() -> dict:
        return {"status": "ok"}

    @router.post("/chat")
    async def chat(req: ChatRequest) -> StreamingResponse:
        conv_id = _parse_optional_conversation_id(req.conversation_id)

        async def generate():
            assistant_parts: list[str] = []
            try:
                async for event in chat_service.stream(
                    messages=req.messages,
                    model=req.model,
                    thinking_budget=req.thinking_budget,
                ):
                    if event.get("type") == "text_delta":
                        assistant_parts.append(event.get("text", ""))
                    event_name = event.pop("type")
                    yield format_event(event_name, event)
            except Exception as exc:
                yield format_event("error", {"message": str(exc)})
                return

            if conv_id is not None:
                _commit_turn(conversation_service, conv_id, req.messages, assistant_parts)

        return StreamingResponse(generate(), media_type="text/event-stream", headers=SSE_HEADERS)

    return router


def _parse_optional_conversation_id(value: str | None) -> ConversationId | None:
    if value is None or value == "":
        return None
    try:
        return ConversationId(value)
    except InvalidConversationId:
        raise HTTPException(status_code=400, detail=f"Invalid conversation_id: {value!r}")


def _commit_turn(
    conversations: ConversationService,
    conv_id: ConversationId,
    request_messages: list[dict],
    assistant_parts: list[str],
) -> None:
    last_user = next(
        (m.get("content", "") for m in reversed(request_messages) if m.get("role") == "user"),
        "",
    )
    assistant_text = "".join(assistant_parts).strip()
    if not (last_user or assistant_text):
        return
    try:
        conversations.add_turn(conv_id, str(last_user), assistant_text)
    except ConversationNotFound:
        log.warning("conversation %s not found while committing turn — turn lost", conv_id.value)
