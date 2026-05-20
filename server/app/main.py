from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routes import chat, lessons


app = FastAPI(title="Study Learning App", version="0.1.0")
app.include_router(chat.router, prefix="/api")
app.include_router(lessons.router, prefix="/api")
# Static files (index.html, css/, js/) — keep mount last so /api routes match first.
app.mount("/", StaticFiles(directory="static", html=True), name="static")
