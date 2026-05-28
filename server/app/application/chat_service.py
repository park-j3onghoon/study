"""Streaming chat use case.

Pure-read: yields agent events, never writes. Persistence is a separate Command
(ConversationService.add_turn) that the route triggers after the stream ends.
"""
from typing import AsyncIterator

from ..domain.ports import Agent


class ChatService:
    def __init__(self, agent: Agent):
        self.agent = agent

    async def stream(
        self,
        messages: list[dict],
        model: str | None = None,
        thinking_budget: int | None = None,
    ) -> AsyncIterator[dict]:
        async for event in self.agent.stream(
            messages=messages,
            model=model,
            thinking_budget=thinking_budget,
        ):
            yield event
