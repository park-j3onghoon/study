from fastapi import FastAPI

from .routes import chat, lessons


app = FastAPI(title="Study Learning App", version="0.1.0")
app.include_router(chat.router, prefix="/api")
app.include_router(lessons.router, prefix="/api")
