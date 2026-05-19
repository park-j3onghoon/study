from fastapi import APIRouter
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
async def chat(req: ChatRequest) -> dict:
    return await agent.run(
        messages=req.messages,
        model=req.model,
        thinking_budget=req.thinking_budget,
    )
