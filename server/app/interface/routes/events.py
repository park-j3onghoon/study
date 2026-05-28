"""SSE endpoint for server-pushed events (file changes etc.)."""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ...domain.ports import EventStream
from ..sse import SSE_HEADERS, format_event


def make_router(event_stream: EventStream) -> APIRouter:
    router = APIRouter()

    @router.get("/events")
    async def events() -> StreamingResponse:
        async def generate():
            try:
                async for event in event_stream.watch():
                    event_name = event.pop("type")
                    yield format_event(event_name, event)
            except Exception as exc:
                yield format_event("error", {"message": str(exc)})

        return StreamingResponse(generate(), media_type="text/event-stream", headers=SSE_HEADERS)

    return router
