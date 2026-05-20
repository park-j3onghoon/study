"""FastAPI app entry. Wires composition root → routes → static files."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .infrastructure.bootstrap import build
from .interface.routes import chat, lessons


app = FastAPI(title="Study Learning App", version="0.2.0")

_state = build()
app.include_router(chat.make_router(_state.chat_service), prefix="/api")
app.include_router(lessons.make_router(_state.lesson_service), prefix="/api")
# /api routes match first; static catch-all is mounted last.
app.mount("/", StaticFiles(directory="static", html=True), name="static")
