"""Chat endpoints. /api/chat는 SSE 스트리밍. /api/health는 단순 헬스체크."""
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..agent import agent


router = APIRouter()


class ChatRequest(BaseModel):
    messages: list[dict]
    model: str | None = None
    thinking_budget: int | None = None


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.post("/chat")
async def chat(req: ChatRequest) -> StreamingResponse:
    async def generate():
        try:
            async for event in agent.stream_run(
                messages=req.messages,
                model=req.model,
                thinking_budget=req.thinking_budget,
            ):
                event_name = event.pop("type")
                yield _format_sse(event_name, event)
        except Exception as exc:
            yield _format_sse("error", {"message": str(exc)})

    # X-Accel-Buffering: no — proxies가 SSE를 버퍼링하지 않도록 (uvicorn 단독이면 무관)
    headers = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    return StreamingResponse(generate(), media_type="text/event-stream", headers=headers)


def _format_sse(event_name: str, data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event_name}\ndata: {payload}\n\n"
