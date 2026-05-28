"""FastAPI app entry. Wires composition root → routes → static files."""
import os

# Force the Claude Code CLI subprocess to use Max OAuth, not a stale ANTHROPIC_API_KEY
# inherited from the shell. We migrated to Claude Max billing — API key path is dead.
os.environ.pop("ANTHROPIC_API_KEY", None)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .infrastructure.bootstrap import build
from .interface.routes import chat, conversations, events, lessons, models


app = FastAPI(title="Study Learning App", version="0.5.0")

_state = build()
app.include_router(
    chat.make_router(_state.chat_service, _state.conversation_service),
    prefix="/api",
)
app.include_router(lessons.make_router(_state.lesson_service), prefix="/api")
app.include_router(conversations.make_router(_state.conversation_service), prefix="/api")
app.include_router(events.make_router(_state.event_stream), prefix="/api")
app.include_router(models.make_router(_state.model_service), prefix="/api")
# /api routes match first; static catch-all is mounted last.
app.mount("/", StaticFiles(directory="static", html=True), name="static")
