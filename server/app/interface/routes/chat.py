"""Chat endpoints (SSE streaming). Depends only on ChatService."""
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ...application.chat_service import ChatService
from ..schemas import ChatRequest


def make_router(chat_service: ChatService) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    async def health() -> dict:
        return {"status": "ok"}

    @router.post("/chat")
    async def chat(req: ChatRequest) -> StreamingResponse:
        async def generate():
            try:
                async for event in chat_service.stream(
                    messages=req.messages,
                    model=req.model,
                    thinking_budget=req.thinking_budget,
                ):
                    event_name = event.pop("type")
                    yield _format_sse(event_name, event)
            except Exception as exc:
                yield _format_sse("error", {"message": str(exc)})

        headers = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
        return StreamingResponse(generate(), media_type="text/event-stream", headers=headers)

    return router


def _format_sse(event_name: str, data: dict) -> str:
    return f"event: {event_name}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
