"""Application service for streaming chat. Thin orchestrator over the Agent port.

Kept as a service (rather than calling Agent directly from routes) so that future
cross-cutting concerns (system prompts, message validation, conversation persistence)
have a clear home without touching the interface layer.
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
