"""SSE endpoint for server-pushed events (file changes etc.)."""
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ...domain.ports import EventStream


def make_router(event_stream: EventStream) -> APIRouter:
    router = APIRouter()

    @router.get("/events")
    async def events() -> StreamingResponse:
        async def generate():
            try:
                async for event in event_stream.watch():
                    event_name = event.pop("type")
                    yield _format_sse(event_name, event)
            except Exception as exc:
                yield _format_sse("error", {"message": str(exc)})

        headers = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
        return StreamingResponse(generate(), media_type="text/event-stream", headers=headers)

    return router


def _format_sse(event_name: str, data: dict) -> str:
    return f"event: {event_name}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
